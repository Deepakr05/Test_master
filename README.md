# ✨ TestMaster — AI Test Orchestrator

TestMaster is a powerful, local-first web application designed to orchestrate your software testing lifecycle. By integrating directly with Jira and leveraging advanced Large Language Models (LLMs), it automatically generates comprehensive, structured test plans and exports them into standard formats.

## 🚀 Key Features

### 1. 🤖 Multi-LLM AI Test Plan Generation
Generate detailed test plans directly from Jira tickets using your choice of LLM. TestMaster parses Jira descriptions, acceptance criteria, and sub-tasks to create an exhaustive plan.
- **Supported Providers**: OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), Google (Gemini 1.5 Pro), Groq, and Local LLMs (via Ollama/LM Studio).
- **Global Model Switcher**: Seamlessly switch your active LLM provider directly from the sidebar on any page, complete with on-demand API key validation.
- **Template Supremacy**: Output meticulously adheres to a strict 13-section Test Plan template (including Scope, Environments, Test Strategy, and Risks & Mitigations).

### 2. 🎫 Seamless Jira Integration
- Input a Jira Issue ID, and TestMaster automatically fetches the issue details securely via the Atlassian REST API.
- Generates context-aware scenarios including automatic inclusion of negative and edge cases.

### 3. 🎭 Playwright E2E Script Generation
- **Automated Scripting**: Select manual test cases and use AI to automatically generate robust, executable **Playwright** End-to-End automation scripts in JavaScript/TypeScript.
- Streamline your transition from manual scenarios to continuous testing.

### 4. 📋 Test Case Dashboard & CRUD
- A centralized dashboard to view, search, and manage individual test cases extracted across all your test plans.
- Full CRUD (Create, Read, Update, Delete) capability allows QAs to manually refine and perfect AI-generated test steps, expected results, and test data.

### 5. 📄 Export & Reporting
- **DOCX Export**: Generates perfectly formatted Microsoft Word documents using `python-docx` mapped directly to standard templates.
- **PDF Export**: Generates clean, professional PDF reports entirely offline using ReportLab.

### 6. 🌓 Modern, Refined User Experience
- Built with React, Vite, and custom CSS variables.
- Features a **Dark / Light mode toggle** that persists user preferences using localStorage. 
- Fast, responsive, glassmorphism-inspired UI with smooth transitions and micro-animations.

### 7. 🔒 Local-First & Privacy-Focused
- 100% local workflow. No cloud synchronization of your proprietary test data.
- State and history run securely through your local filesystem (`data/history.json`).
- API Keys are masked and read from local environments securely.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, React Router, Axios |
| Backend | Flask (Python 3.12) |
| Styling | Custom CSS (Dark/Light mode native) |
| LLM Integration | Direct REST clients for OpenAI, Anthropic, Google Gemini |
| Exports | `python-docx` (Word), `reportlab` (PDF) |

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.12+
- Node.js & npm (for the frontend)

### Backend Setup
1. Clone the repository and navigate to the project root.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask server:
   ```bash
   python server.py
   ```
   *The backend runs on `http://localhost:5000`*

### Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory.
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend runs on `http://localhost:3000`*

### Configuration
- Navigate to the **Settings** page in the application to add your Jira connection details and your API keys for preferred LLM providers. Have fun testing!
