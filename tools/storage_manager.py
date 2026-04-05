"""
storage_manager.py — Layer 3 Tool
Manages all local file persistence: history.json, settings.json.
SOP: architecture/storage_sop.md
"""
import json
import os
from datetime import datetime
from pathlib import Path
try:
    from supabase import create_client, Client
except ImportError:
    Client = None

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
EXPORTS_DIR = DATA_DIR / "exports"

# Ensure directories exist locally (fails gracefully on cloud Read-Only filesystems like Vercel)
try:
    DATA_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)
except OSError:
    pass

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key and Client:
        return create_client(url, key)
    return None

# ─── Default structures ───────────────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "jira": {
        "base_url": "",
        "email": "",
        "api_token": ""
    },
    "llm": {
        "active_provider": "openai",
        "providers": {
            "openai": {
                "api_key": "",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "anthropic": {
                "api_key": "",
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "google": {
                "api_key": "",
                "model": "gemini-1.5-pro",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "groq": {
                "api_key": "",
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "local_llm": {
                "api_key": "not-needed",
                "base_url": "http://localhost:11434/v1",
                "model": "llama3",
                "temperature": 0.7,
                "max_tokens": 4096
            }
        }
    }
}


# ─── Settings ────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """Load settings from Supabase (if available), then local JSON, with env overrides."""
    merged = DEFAULT_SETTINGS.copy()
    
    # 1. Try Supabase
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("settings").select("config").eq("id", "global").execute()
            if res.data and res.data[0].get("config"):
                _deep_merge(merged, res.data[0]["config"])
        except Exception as e:
            print(f"Supabase settings load error: {e}")

    # 2. Try Local (Fallback/Dev)
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                stored = json.load(f)
            _deep_merge(merged, stored)
        except Exception as e:
            print(f"Local settings load error: {e}")

    # 3. Vercel env overrides (Highest Priority)
    if os.getenv("OPENAI_API_KEY"): merged["llm"]["providers"]["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"): merged["llm"]["providers"]["anthropic"]["api_key"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GEMINI_API_KEY"): merged["llm"]["providers"]["google"]["api_key"] = os.getenv("GEMINI_API_KEY")
    if os.getenv("GROQ_API_KEY"): merged["llm"]["providers"]["groq"]["api_key"] = os.getenv("GROQ_API_KEY")
    if os.getenv("JIRA_API_TOKEN"): merged["jira"]["api_token"] = os.getenv("JIRA_API_TOKEN")
    if os.getenv("JIRA_EMAIL"): merged["jira"]["email"] = os.getenv("JIRA_EMAIL")
    if os.getenv("JIRA_BASE_URL"): merged["jira"]["base_url"] = os.getenv("JIRA_BASE_URL")
    
    return merged


def save_settings(settings: dict) -> None:
    """Persist settings to Supabase and attempt local save."""
    # 1. Supabase (Primary for Cloud)
    sb = get_supabase()
    if sb:
        try:
            sb.table("settings").upsert({"id": "global", "config": settings}).execute()
        except Exception as e:
            print(f"Supabase settings save error: {e}")

    # 2. Local (Primary for Dev, fails gracefully on Vercel)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Local settings save suppressed (expected on Vercel): {e}")


def get_settings_masked() -> dict:
    """Return settings with API keys masked (last 4 chars visible)."""
    settings = load_settings()
    masked = json.loads(json.dumps(settings))  # deep copy

    # Mask Jira token
    tok = masked.get("jira", {}).get("api_token", "")
    masked["jira"]["api_token"] = _mask_key(tok)

    # Mask LLM keys
    for provider in masked.get("llm", {}).get("providers", {}).values():
        provider["api_key"] = _mask_key(provider.get("api_key", ""))

    return masked


def _mask_key(key: str) -> str:
    if not key or len(key) <= 4:
        return "••••"
    return "••••••••••••" + key[-4:]


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


# ─── History ─────────────────────────────────────────────────────────────────

def load_history() -> list:
    """Load all test plan records from Supabase (if configured) or local JSON."""
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("test_plans").select("*").execute()
            records = res.data or []
            return sorted(records, key=lambda r: r.get("generated_at", ""), reverse=True)
        except Exception as e:
            print(f"Supabase read error: {e}")
            
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_test_plan(record: dict) -> None:
    """Append a test plan record to Supabase and/or history.json."""
    sb = get_supabase()
    if sb:
        try:
            sb.table("test_plans").upsert(record).execute()
        except Exception as e:
            print(f"Supabase upsert error: {e}")

    history = load_history()
    # Update if same ID exists, otherwise append
    existing_ids = [r["id"] for r in history]
    if record["id"] in existing_ids:
        history = [record if r["id"] == record["id"] else r for r in history]
    else:
        history.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        try:
            json.dump(history, f, indent=2, ensure_ascii=False)
        except OSError:
            pass


def get_test_plan(plan_id: str) -> dict | None:
    """Find and return a single test plan by ID."""
    history = load_history()
    for record in history:
        if record["id"] == plan_id:
            return record
    return None


def delete_test_plan(plan_id: str) -> bool:
    """Remove a test plan by ID. Returns True if deleted."""
    sb = get_supabase()
    if sb:
        try:
            sb.table("test_plans").delete().eq("id", plan_id).execute()
        except Exception as e:
            print(f"Supabase delete error: {e}")

    history = load_history()
    new_history = [r for r in history if r["id"] != plan_id]
    if len(new_history) == len(history):
        return False
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        try:
            json.dump(new_history, f, indent=2, ensure_ascii=False)
        except OSError:
            pass
    return True


def next_id() -> str:
    """Generate the next unique test plan ID: TP-YYYYMMDD-NNN."""
    today = datetime.now().strftime("%Y%m%d")
    history = load_history()
    today_records = [r for r in history if r.get("id", "").startswith(f"TP-{today}-")]
    seq = len(today_records) + 1
    return f"TP-{today}-{seq:03d}"


def get_stats() -> dict:
    """Compute dashboard statistics from history."""
    history = load_history()
    completed = [r for r in history if r.get("status") == "completed"]
    settings = load_settings()

    total_time = sum(r.get("generation_time_seconds", 0) for r in completed)
    avg_time = round(total_time / len(completed), 1) if completed else 0.0

    # Count unique Jira IDs
    jira_ids = set(r.get("jira_id", "") for r in history)

    active_provider = settings.get("llm", {}).get("active_provider", "openai")
    active_model = (
        settings.get("llm", {})
        .get("providers", {})
        .get(active_provider, {})
        .get("model", "GPT-4o")
    )

    return {
        "total_plans": len(history),
        "jira_issues_processed": len(jira_ids),
        "avg_generation_time": avg_time,
        "active_model": active_model,
        "active_provider": active_provider,
        "recent": history[-10:][::-1],  # last 10, newest first
    }
