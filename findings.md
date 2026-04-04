# 🔍 findings.md — Research, Discoveries & Constraints
> Updated: 2026-04-04

---

## 📄 Template Structure Discovery

**Source:** `Template/Test Plan - Template.docx`
**Extraction Method:** python-docx

The template has **13 mandatory sections** in a strict hierarchy:

| # | Section | Level | Notes |
|---|---------|-------|-------|
| 1 | Objective | H2 | Overview, purpose, goals |
| 2 | Scope | H2 | Container for sub-sections |
| 3 | Inclusions | H3 | Features/pages in scope |
| 4 | Test Environments | H3 | OS, Browser, Device, Network table |
| 5 | Defect Reporting Procedure | H3 | POC table + JIRA tooling |
| 6 | Test Strategy | H3 | 3 steps + testing types |
| 7 | Test Schedule | H3 | Sprint-based table |
| 8 | Test Deliverables | H3 | List of artefacts |
| 9 | Entry and Exit Criteria | H3 | 3 sub-phases |
| 10 | Test Execution | H3 | Entry/Exit H4 |
| 11 | Test Closure | H3 | Entry/Exit H4 |
| 12 | Tools | H4 | JIRA, Mind map etc. |
| 13 | Risks and Mitigations | H4 | Risk/Mitigation table |
| 14 | Approvals | H4 | Document approval list |

**Tables in template:**
- **Table 1:** Environment URLs (Name | Env URL | columns)
- **Table 2:** Defect POC table (Defect Process | POC)
- **Table 3:** Test Schedule (Task | Dates)

**Unicode issue:** Some bullet characters (▪) cause cp1252 encoding errors — must use `sys.stdout.reconfigure(encoding='utf-8')`.

---

## 🔗 Jira REST API v3 — Key Findings

- **Base URL:** `https://{your-domain}.atlassian.net/rest/api/3/issue/{issueIdOrKey}`
- **Auth:** Basic Auth with email + API token (base64 encoded)
- **Header:** `Authorization: Basic {base64(email:token)}`
- **Key fields:** `summary`, `description`, `priority`, `assignee`, `reporter`, `labels`, `subtasks`, `status`, `issuetype`, `customfield_10016` (story points)
- **Description format:** Jira returns description as Atlassian Document Format (ADF) — need to parse `.content[].content[].text` recursively
- **Rate Limits:** 10 requests/sec per user (well within our usage)

---

## 🤖 LLM Integration Findings

### OpenAI (GPT-4o)
- Library: `openai` (pip)
- Auth: `OPENAI_API_KEY` env var
- Max context: 128k tokens (GPT-4o)
- Endpoint: `https://api.openai.com/v1/chat/completions`

### Anthropic (Claude 3.5 Sonnet)
- Library: `anthropic` (pip)
- Auth: `ANTHROPIC_API_KEY` env var  
- Max context: 200k tokens
- Endpoint: `https://api.anthropic.com/v1/messages`

### Google (Gemini 1.5 Pro)
- Library: `google-generativeai` (pip)
- Auth: `GOOGLE_API_KEY` env var
- Max context: 1M tokens

**Prompt Strategy:** Use a structured system prompt referencing each template section, with the Jira issue JSON injected as context. Ask LLM to fill in each section as JSON, then map to template.

---

## 📦 Export Engine Findings

### DOCX (python-docx)
- `pip install python-docx`
- Can programmatically add headings, paragraphs, and tables
- Must match heading styles: Heading 1, Heading 2, Heading 3, Heading 4, Normal
- Strategy: Load original template → clear content → write new content preserving styles

### PDF (reportlab or weasyprint)
- **weasyprint** preferred: Convert DOCX → HTML → PDF
- Alternative: Use `docx2pdf` for direct conversion (requires MS Word or LibreOffice)
- V1 approach: Generate HTML from test plan JSON → convert to PDF with weasyprint

---

## 🗄️ Storage Findings

- **history.json:** Append-only array of test plan records. Load on startup, write on each generation.
- **settings.json:** Single object, overwritten on save. API keys masked in UI (show only last 4 chars).
- **exports/:** Named `{JIRA_ID}_{YYYYMMDD}.{ext}` for easy identification.

---

## 🎨 UI/UX Findings (from design screenshots)

- **App name:** TestForge
- **Color palette:** #0D1117 (bg), #161B22 (card), #00E5CC (cyan accent), #FF6B6B (error/failed), #FFA500 (warning/in-progress)
- **Font:** Appears to be Inter or similar sans-serif
- **Status colors:** Completed=green, In Progress=blue, Failed=red/orange, Pending=gray
- **Nav items:** Dashboard, Generate, History, Settings
- **LLM badges:** Color-coded by provider (OpenAI=green, Anthropic=orange, Google=blue)

---

## ⚠️ Constraints

1. **No Jira write-back in V1** — export only
2. **Local storage only** — no external databases
3. **Template is immutable** — no extra sections allowed
4. **Python must be ≥3.12** — installed 2026-04-04
5. **API keys must never appear in frontend HTML/JS**
