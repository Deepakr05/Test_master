"""
server.py — Layer 2 Navigation (Flask API)
Routes all requests between frontend and Layer 3 tools.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

# Ensure tools/ is importable
sys.path.insert(0, str(Path(__file__).parent))

from tools.storage_manager import (
    load_settings, save_settings, get_settings_masked,
    load_history, get_test_plan, delete_test_plan, get_stats,
)
from tools.jira_client import fetch_issue, test_connection as jira_test_connection
from tools.llm_client import test_connection as llm_test_connection
from tools.test_plan_generator import generate_test_plan
from tools.export_engine import to_docx, to_pdf

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ─── Helpers ──────────────────────────────────────────────────────────────────

def ok(data=None, **kwargs):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return jsonify(payload)


def err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def stats():
    """Dashboard statistics: total plans, jira issues, avg time, active model."""
    try:
        return ok(get_stats())
    except Exception as e:
        return err(str(e), 500)


# ─── Jira ────────────────────────────────────────────────────────────────────

@app.route("/api/jira/issue/<string:issue_id>", methods=["GET"])
def jira_issue(issue_id: str):
    """Fetch and return a Jira issue preview."""
    try:
        settings = load_settings()
        issue = fetch_issue(issue_id.upper(), settings)
        return ok(issue)
    except ValueError as e:
        return err(str(e), 400)
    except Exception as e:
        return err(f"Unexpected error: {e}", 500)


# ─── Generate ────────────────────────────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Full test plan generation pipeline.
    Body: { jira_issue_id, llm_provider, include_sub_tasks, include_negative_cases,
            detail_level, test_plan_format }
    """
    try:
        body = request.get_json(force=True) or {}
        if not body.get("jira_issue_id"):
            return err("jira_issue_id is required")

        record = generate_test_plan(body)
        return ok(record)
    except ValueError as e:
        return err(str(e), 400)
    except RuntimeError as e:
        return err(str(e), 502)
    except Exception as e:
        return err(f"Unexpected error: {e}", 500)


# ─── History ─────────────────────────────────────────────────────────────────

@app.route("/api/history", methods=["GET"])
def history():
    """
    List all test plans, optionally filtered.
    Query params: q (search), filter (all|week|month|starred)
    """
    try:
        q = request.args.get("q", "").lower()
        f = request.args.get("filter", "all")

        records = load_history()
        records = sorted(records, key=lambda r: r.get("generated_at", ""), reverse=True)

        # Filter by date
        now = datetime.utcnow()
        if f == "week":
            records = [r for r in records if _within_days(r.get("generated_at", ""), 7)]
        elif f == "month":
            records = [r for r in records if _within_days(r.get("generated_at", ""), 30)]
        elif f == "starred":
            records = [r for r in records if r.get("starred", False)]

        # Search filter
        if q:
            records = [
                r for r in records
                if q in r.get("jira_id", "").lower()
                or q in r.get("jira_title", "").lower()
                or q in r.get("title", "").lower()
            ]

        # Return summary view (no full markdown for list performance)
        summary = [{
            "id": r["id"],
            "jira_id": r.get("jira_id", ""),
            "jira_title": r.get("jira_title", ""),
            "title": r.get("title", ""),
            "llm_provider": r.get("llm_provider", ""),
            "llm_model": r.get("llm_model", ""),
            "status": r.get("status", ""),
            "generated_at": r.get("generated_at", ""),
            "test_case_count": r.get("test_case_count", 0),
            "generation_time_seconds": r.get("generation_time_seconds", 0),
            "starred": r.get("starred", False),
        } for r in records]

        return ok(summary)
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/test-cases", methods=["GET"])
def all_test_cases():
    """
    Return a flattened list of all test cases across all plans.
    Used for the Test Cases Dashboard.
    """
    try:
        from tools.storage_manager import load_history
        records = load_history()
        
        test_cases = []
        for r in records:
            tcs = r.get("content", {}).get("test_cases", [])
            for tc in tcs:
                tc_copy = dict(tc)
                # Enrich with plan data
                tc_copy["plan_id"] = r["id"]
                tc_copy["jira_id"] = r.get("jira_id", "")
                tc_copy["jira_title"] = r.get("jira_title", "")
                tc_copy["generated_at"] = r.get("generated_at", "")
                test_cases.append(tc_copy)
                
        # Sort by generated_at descending primarily
        test_cases.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        return ok(test_cases)
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/test-cases/<string:plan_id>", methods=["POST"])
def tc_create(plan_id: str):
    try:
        from tools.storage_manager import save_test_plan
        record = get_test_plan(plan_id)
        if not record: return err("Plan not found", 404)
        
        body = request.get_json(force=True) or {}
        # Generate new TC-XXX ID based on max existing
        tcs = record.get("content", {}).setdefault("test_cases", [])
        max_num = 0
        for tc in tcs:
            if tc.get("id", "").startswith("TC-"):
                try:
                    num = int(tc["id"].replace("TC-", ""))
                    max_num = max(max_num, num)
                except:
                    pass
        
        new_id = f"TC-{max_num + 1:03d}"
        new_tc = {
            "id": new_id,
            "title": body.get("title", "New Test Case"),
            "priority": body.get("priority", "Medium"),
            "type": body.get("type", "Positive"),
            "preconditions": body.get("preconditions", []),
            "steps": body.get("steps", []),
            "expected_result": body.get("expected_result", ""),
            "test_data": body.get("test_data", {})
        }
        tcs.append(new_tc)
        record["test_case_count"] = len(tcs)
        save_test_plan(record)
        return ok(new_tc)
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/test-cases/<string:plan_id>/<string:tc_id>", methods=["PUT"])
def tc_update(plan_id: str, tc_id: str):
    try:
        from tools.storage_manager import save_test_plan
        record = get_test_plan(plan_id)
        if not record: return err("Plan not found", 404)
        
        body = request.get_json(force=True) or {}
        tcs = record.get("content", {}).get("test_cases", [])
        
        for idx, tc in enumerate(tcs):
            if tc.get("id") == tc_id:
                tcs[idx] = body  # Replace with the updated JSON payload
                record["content"]["test_cases"] = tcs
                save_test_plan(record)
                return ok(body)
                
        return err("Test case not found", 404)
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/test-cases/<string:plan_id>/<string:tc_id>", methods=["DELETE"])
def tc_delete(plan_id: str, tc_id: str):
    try:
        from tools.storage_manager import save_test_plan
        record = get_test_plan(plan_id)
        if not record: return err("Plan not found", 404)
        
        tcs = record.get("content", {}).get("test_cases", [])
        initial_len = len(tcs)
        tcs = [tc for tc in tcs if tc.get("id") != tc_id]
        
        if len(tcs) == initial_len:
            return err("Test case not found", 404)
            
        record["content"]["test_cases"] = tcs
        record["test_case_count"] = len(tcs)
        save_test_plan(record)
        return ok({"deleted": tc_id})
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/history/<string:plan_id>", methods=["GET"])
def history_detail(plan_id: str):
    """Get full test plan record including markdown content."""
    try:
        record = get_test_plan(plan_id)
        if not record:
            return err(f"Test plan '{plan_id}' not found", 404)
        return ok(record)
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/history/<string:plan_id>", methods=["DELETE"])
def history_delete(plan_id: str):
    """Delete a test plan by ID."""
    try:
        deleted = delete_test_plan(plan_id)
        if not deleted:
            return err(f"Test plan '{plan_id}' not found", 404)
        return ok({"deleted": plan_id})
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/history/<string:plan_id>/star", methods=["PATCH"])
def history_star(plan_id: str):
    """Toggle starred status on a test plan."""
    try:
        from tools.storage_manager import load_history, save_test_plan
        record = get_test_plan(plan_id)
        if not record:
            return err(f"Test plan '{plan_id}' not found", 404)
        record["starred"] = not record.get("starred", False)
        save_test_plan(record)
        return ok({"starred": record["starred"]})
    except Exception as e:
        return err(str(e), 500)


# ─── Export ───────────────────────────────────────────────────────────────────

@app.route("/api/export/<string:plan_id>/<string:fmt>", methods=["GET"])
def export(plan_id: str, fmt: str):
    """Export test plan as docx or pdf. Streams the file."""
    if fmt not in ("docx", "pdf"):
        return err("Format must be 'docx' or 'pdf'")
    try:
        record = get_test_plan(plan_id)
        if not record:
            return err(f"Test plan '{plan_id}' not found", 404)

        from tools.storage_manager import save_test_plan as _save
        if fmt == "docx":
            path = to_docx(record)
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            path = to_pdf(record)
            mime = "application/pdf"

        # Store export path
        record.setdefault("export_paths", {})[fmt] = path
        _save(record)

        filename = Path(path).name
        return send_file(path, mimetype=mime, as_attachment=True, download_name=filename)
    except Exception as e:
        return err(f"Export failed: {e}", 500)


# ─── Settings ─────────────────────────────────────────────────────────────────

@app.route("/api/settings", methods=["GET"])
def settings_get():
    """Return settings with masked API keys."""
    try:
        return ok(get_settings_masked())
    except Exception as e:
        return err(str(e), 500)


@app.route("/api/settings", methods=["PUT"])
def settings_put():
    """
    Save settings. Client sends full settings including NEW (unmasked) keys.
    Masked values (starting with ••) are preserved from current stored settings.
    """
    try:
        incoming = request.get_json(force=True) or {}
        current = load_settings()

        # Merge: if key starts with ••, keep the stored value
        _merge_preserving_masked(current, incoming)

        save_settings(current)
        return ok(get_settings_masked())
    except Exception as e:
        return err(str(e), 500)


def _merge_preserving_masked(current: dict, incoming: dict, path=""):
    """Recursively merge incoming into current, skipping masked (••) values."""
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(current.get(key), dict):
            _merge_preserving_masked(current[key], value, path=f"{path}.{key}")
        elif isinstance(value, str) and value.startswith("••"):
            pass  # Keep existing stored value
        else:
            current[key] = value


@app.route("/api/settings/test-connection", methods=["POST"])
def settings_test():
    """
    Test LLM or Jira connection.
    Body: { type: 'llm' | 'jira', provider?: 'openai' | 'anthropic' | 'google' }
    """
    try:
        body = request.get_json(force=True) or {}
        connection_type = body.get("type", "llm")
        settings = load_settings()

        if connection_type == "jira":
            result = jira_test_connection(settings)
        else:
            provider = body.get("provider", settings["llm"]["active_provider"])
            result = llm_test_connection(provider, settings)

        return ok(result)
    except Exception as e:
        return err(str(e), 500)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _within_days(iso_str: str, days: int) -> bool:
    try:
        from datetime import timezone, timedelta
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return dt >= cutoff
    except Exception:
        return False


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("[TestMaster] API starting on http://localhost:5000")
    app.run(debug=True, port=5000, host="0.0.0.0")
