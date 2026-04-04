# Jira Integration SOP
## Goal
Fetch a Jira issue by ID using REST API v3 and return normalized data (Schema 2).

## Input
- `issue_id`: string (e.g., "PROJ-1042")
- `settings`: dict loaded from `data/settings.json`

## Tool
`tools/jira_client.py → fetch_issue()`

## Auth Method
Basic Auth: `base64(email:api_token)` in `Authorization` header.

## Endpoint
`GET {base_url}/rest/api/3/issue/{issueIdOrKey}`

## Description Parsing
Jira returns descriptions as Atlassian Document Format (ADF) — a nested JSON structure.
Use `_parse_adf_node()` recursively to extract plain text.

## Error Handling
| Status | Action |
|--------|--------|
| 401 | Return "Authentication failed. Check email and token." |
| 404 | Return "Issue not found. Check the issue ID." |
| 403 | Return "Access denied. Insufficient token permissions." |
| Timeout | Return "Connection timed out." |
| Any other | Return "Jira API error {code}" |

## Rate Limits
- 10 req/sec per user — well within usage for this app
- No throttling needed in V1

## Edge Cases
- `sub_tasks` may be empty list — always return `[]` not `null`
- `story_points` may be under `customfield_10016` OR `customfield_10028` — try both
- `acceptance_criteria` is rarely in a standard field — parse from description if not found

## Connection Test
`GET {base_url}/rest/api/3/myself` — returns user info if auth is valid.
