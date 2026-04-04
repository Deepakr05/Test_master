# 📋 task_plan.md — TestForge Build Plan
> B.L.A.S.T. Framework | V1.0 | Started: 2026-04-04

---

## ✅ Phase 0: Initialization (COMPLETE)
- [x] Read B.L.A.S.T. framework
- [x] Reviewed all 5 UI screens (Dashboard, Generate, Loading, History, Settings, View Test Plan)
- [x] Conducted 5 Discovery Questions
- [x] Extracted Test Plan template structure (13 sections)
- [x] Installed Python 3.12
- [x] Created `gemini.md` (Project Constitution)
- [x] Created `task_plan.md` (this file)
- [x] Created `findings.md`
- [x] Created `progress.md`

---

## 🏗️ Phase 1: B — Blueprint (COMPLETE)
- [x] North Star defined
- [x] Integrations scoped (Jira V1, all 3 LLMs configurable)
- [x] Source of truth decided (local file-based)
- [x] Delivery payload defined (DOCX + PDF export)
- [x] Behavioral rules locked (strict template adherence)
- [x] Data schema defined in `gemini.md`

---

## ⚡ Phase 2: L — Link (Connectivity)
- [ ] Create `.env` template
- [ ] Build `tools/jira_client.py` — test Jira API connection
- [ ] Build `tools/llm_client.py` — test OpenAI/Anthropic/Google connections
- [ ] Verify all connections respond correctly before proceeding
- [ ] Write architecture SOP for each integration

---

## ⚙️ Phase 3: A — Architect (3-Layer Build)

### Layer 1: Architecture SOPs
- [ ] `architecture/jira_integration_sop.md`
- [ ] `architecture/llm_generation_sop.md`
- [ ] `architecture/export_sop.md`
- [ ] `architecture/storage_sop.md`

### Layer 2: Navigation (Flask Server)
- [ ] `server.py` — Flask API with all routes
  - [ ] `GET  /api/stats` — Dashboard stats
  - [ ] `GET  /api/jira/issue/<id>` — Fetch & preview Jira issue
  - [ ] `POST /api/generate` — Generate test plan
  - [ ] `GET  /api/history` — List all test plans
  - [ ] `GET  /api/history/<id>` — Get single test plan
  - [ ] `GET  /api/export/<id>/<format>` — Export DOCX/PDF
  - [ ] `GET  /api/settings` — Get settings
  - [ ] `PUT  /api/settings` — Save settings
  - [ ] `POST /api/settings/test-connection` — Test LLM/Jira connection

### Layer 3: Tools
- [ ] `tools/jira_client.py` — fetch_issue(), list_sub_tasks()
- [ ] `tools/llm_client.py` — generate_test_plan(), supports openai/anthropic/google
- [ ] `tools/test_plan_generator.py` — orchestrates fetch → prompt → parse
- [ ] `tools/export_engine.py` — to_docx(), to_pdf() using template
- [ ] `tools/storage_manager.py` — save/load history.json and settings.json

---

## ✨ Phase 4: S — Stylize (Frontend)

### Pages (matching UI designs)
- [ ] **Dashboard** (`index.html` default view)
  - [ ] Stats cards (Test Plans Generated, Issues Processed, Avg Time, Active Model)
  - [ ] Recent test plans table (Jira ID, Status, Model, Date)
  - [ ] Quick Generate panel (right side)
  - [ ] Timeline activity feed
- [ ] **Generate Page**
  - [ ] Jira Issue ID input + fetch button
  - [ ] Jira Issue Preview card (title, description, labels, priority)
  - [ ] Test Plan Configuration panel (LLM model, format toggles, toggles)
  - [ ] Generate Test Plan button (full width, cyan)
- [ ] **Loading State**
  - [ ] 4-step progress (Fetching → Analyzing → Drafting → Finalizing)
  - [ ] Animated brain/neural graphic
  - [ ] Loading skeleton bars
- [ ] **History Page**
  - [ ] Search + filter tabs (All, This Week, This Month, Starred)
  - [ ] Table with Jira ID, Title, Model, Test Cases, Date
  - [ ] Right-side preview panel + Copy + Sync buttons
  - [ ] Export CSV button
- [ ] **Settings Page**
  - [ ] LLM model cards (GPT-4o, Claude, Gemini) with connect status
  - [ ] LLM Configuration panel (API key, model version, temperature, max tokens)
  - [ ] Test Connection button
  - [ ] Jira Integration sub-page
  - [ ] Output Formats sub-page
  - [ ] Team and Access sub-page
- [ ] **View Test Plan Page**
  - [ ] Jira ID badge + title + breadcrumb back
  - [ ] Share, Export, Regenerate buttons
  - [ ] Left outline nav (Outline, Statistics, Constraints, Test Data)
  - [ ] High-Level Test Scenarios section
  - [ ] Test Case Details cards (preconditions, steps, expected result, test data)
  - [ ] Jump Links panel (Total, Reviewed, Passed, Summary)
  - [ ] Progress bar (X of N reviewed)

### CSS Design System
- [ ] Dark theme (#0D1117 base, #161B22 cards)
- [ ] Cyan accent (#00E5CC / #00C9B1)
- [ ] Inter/Roboto font via Google Fonts
- [ ] Glassmorphism cards
- [ ] Smooth hover + transition animations
- [ ] Responsive layout

---

## 🛰️ Phase 5: T — Trigger (Deployment)
- [ ] `requirements.txt` with all Python dependencies
- [ ] `README.md` — Setup and run instructions
- [ ] Final end-to-end test with real Jira issue
- [ ] Finalize Maintenance Log in `gemini.md`

---

## 📊 Overall Progress

| Phase | Status |
|-------|--------|
| 0 — Initialization | ✅ Complete |
| 1 — Blueprint | ✅ Complete |
| 2 — Link | ⏳ Pending |
| 3 — Architect | ⏳ Pending |
| 4 — Stylize | ⏳ Pending |
| 5 — Trigger | ⏳ Pending |
