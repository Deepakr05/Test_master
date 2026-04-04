"""
jira_client.py — Layer 3 Tool
Fetches Jira issue data via REST API v3.
SOP: architecture/jira_integration_sop.md
"""
import requests
import base64
import json
import re
from typing import Optional


def _make_auth_header(email: str, token: str) -> dict:
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _parse_adf_node(node: dict) -> str:
    """Recursively extract plain text from Atlassian Document Format (ADF)."""
    if not node:
        return ""
    node_type = node.get("type", "")
    content = node.get("content", [])
    text = node.get("text", "")

    if node_type == "text":
        return text
    if node_type in ("paragraph", "heading"):
        return " ".join(_parse_adf_node(c) for c in content) + "\n"
    if node_type == "bulletList":
        return "\n".join(f"• {_parse_adf_node(item)}" for item in content)
    if node_type == "listItem":
        return " ".join(_parse_adf_node(c) for c in content)
    if node_type == "doc":
        return "\n".join(_parse_adf_node(c) for c in content)
    # Fallback: join all child text
    return " ".join(_parse_adf_node(c) for c in content)


def _parse_description(raw) -> str:
    """Handle both ADF (dict) and plain string descriptions."""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return _parse_adf_node(raw).strip()
    return ""


def fetch_issue(issue_id: str, settings: dict) -> dict:
    """
    Fetch a Jira issue and return it as a normalized dict (Schema 2).
    Raises ValueError on auth/not-found errors.
    """
    base_url = settings.get("jira", {}).get("base_url", "").rstrip("/")
    email = settings.get("jira", {}).get("email", "")
    token = settings.get("jira", {}).get("api_token", "")

    if not all([base_url, email, token]):
        raise ValueError("Jira settings incomplete. Please configure in Settings.")

    url = f"{base_url}/rest/api/3/issue/{issue_id}"
    headers = _make_auth_header(email, token)

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Cannot connect to Jira at {base_url}. Check the URL.")
    except requests.exceptions.Timeout:
        raise ValueError("Jira request timed out. Try again.")

    if response.status_code == 401:
        raise ValueError("Jira authentication failed. Check your email and API token.")
    if response.status_code == 404:
        raise ValueError(f"Issue '{issue_id}' not found. Check the issue ID.")
    if response.status_code == 403:
        raise ValueError("Access denied. Your token may lack permission to read this issue.")
    if not response.ok:
        raise ValueError(f"Jira API error {response.status_code}: {response.text[:200]}")

    raw = response.json()
    fields = raw.get("fields", {})

    # Extract sub-tasks
    sub_tasks = [
        {"id": st.get("key", ""), "title": st.get("fields", {}).get("summary", "")}
        for st in fields.get("subtasks", [])
    ]

    # Acceptance criteria from description or custom field
    description = _parse_description(fields.get("description"))
    acceptance_criteria = ""
    # Try common custom field for acceptance criteria
    for field_key in ["customfield_10016", "customfield_10018", "customfield_10014"]:
        val = fields.get(field_key)
        if val and isinstance(val, (str, dict)):
            if "accept" in field_key.lower() or field_key == "customfield_10018":
                acceptance_criteria = _parse_description(val)
                break

    assignee = fields.get("assignee") or {}
    reporter = fields.get("reporter") or {}

    return {
        "id": raw.get("key", issue_id),
        "title": fields.get("summary", ""),
        "description": description,
        "priority": (fields.get("priority") or {}).get("name", "Medium"),
        "assignee": assignee.get("displayName", "Unassigned"),
        "reporter": reporter.get("displayName", "Unknown"),
        "status": (fields.get("status") or {}).get("name", "Unknown"),
        "issue_type": (fields.get("issuetype") or {}).get("name", "Story"),
        "labels": fields.get("labels", []),
        "story_points": fields.get("customfield_10016") or fields.get("customfield_10028") or 0,
        "acceptance_criteria": acceptance_criteria,
        "sub_tasks": sub_tasks,
        "created_at": fields.get("created", ""),
        "updated_at": fields.get("updated", ""),
    }


def test_connection(settings: dict) -> dict:
    """Verify Jira credentials by calling the /myself endpoint."""
    base_url = settings.get("jira", {}).get("base_url", "").rstrip("/")
    email = settings.get("jira", {}).get("email", "")
    token = settings.get("jira", {}).get("api_token", "")

    if not all([base_url, email, token]):
        return {"ok": False, "error": "Jira settings incomplete."}

    url = f"{base_url}/rest/api/3/myself"
    headers = _make_auth_header(email, token)

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.ok:
            user = response.json()
            return {"ok": True, "user": user.get("displayName", email)}
        return {"ok": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
