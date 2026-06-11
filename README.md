# 🚀 HackPilot

> **AI-powered hackathon copilot for students.**  
> Go from theme to pitch in minutes — with Gemini 2.5 Flash (or a local Ollama model) doing the heavy lifting.

---

## Features

| Tab | Feature | What it does |
|-----|---------|--------------|
| 💡 Ideas | Idea Generator | 5 project ideas with innovation scores & difficulty |
| 🔍 Feasibility | Feasibility Analyzer | Risks & recommendations for your chosen idea |
| 🗓 Plan | Execution Planner | MVP scope, stretch goals, and time-boxed milestones |
| 🎤 Pitch | Elevator Pitch | 60-second spoken pitch + punchy tagline |
| 📄 README | README Generator | GitHub README draft ready to paste |

---

## What's New

### 🌐 Indian Language Support
HackPilot can generate all content in **English**, **Hindi (हिन्दी)**, or **Marathi (मराठी)**.  
Select your language from the sidebar — Gemini's multilingual capability handles translation natively. No external translation APIs required.

### 🤖 Local AI with Ollama
Run HackPilot entirely offline using **Ollama**.  
Select *Ollama (Local)* in the sidebar and choose from `qwen2.5-coder:7b`, `llama3`, `mistral`, or any custom model tag. Make sure Ollama is running first:

```bash
ollama serve
ollama pull llama3   # or whichever model you choose
```

### 🔑 Bring Your Own Key (BYOK)
You can supply your own **Gemini API key** directly in the sidebar instead of configuring secrets. Key resolution order:
1. Key entered in the sidebar (highest priority)
2. `GEMINI_API_KEY` in Streamlit secrets
3. Clear error message with instructions

Your key is handled as a password field and is never logged or stored.

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/your-org/hackpilot.git
cd hackpilot
pip install -r requirements.txt
```

### 2. Configure your Gemini API key

**Option A — Streamlit secrets (recommended for deployment)**

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and set:
# GEMINI_API_KEY = "your-key-here"
```

Get a free key at <https://aistudio.google.com/app/apikey>.

**Option B — BYOK (no config needed)**  
Leave secrets empty and paste your key into the *Gemini API Key* field in the app sidebar at runtime.

**Option C — Ollama (no key needed)**  
Select *Ollama (Local)* in the sidebar and skip API key setup entirely.

### 3. Run

```bash
streamlit run app.py
```

---

## Project Structure

```
hackpilot/
├── app.py                        # Streamlit entry point
├── requirements.txt
├── pyproject.toml                # black / ruff / mypy / pytest config
├── hackpilot/
│   ├── models.py                 # Dataclasses (HackathonContext, ProjectIdea, …)
│   ├── ai_provider.py            # ★ Unified AI service layer (Gemini + Ollama)
│   ├── language.py               # ★ Language enum & prompt instruction builders
│   ├── gemini.py                 # Legacy Gemini wrapper (kept for compatibility)
│   ├── prompts.py                # Prompt builders for all 5 features (+ language)
│   └── features/
│       ├── idea_generator.py     # F1
│       ├── feasibility.py        # F2
│       ├── planner.py            # F3
│       ├── pitch.py              # F4
│       └── readme_gen.py         # F5
├── tests/
│   ├── test_idea_generator.py
│   ├── test_feasibility.py
│   ├── test_planner.py
│   ├── test_pitch.py
│   ├── test_readme_gen.py
│   └── test_enhancements.py      # ★ Language / provider / BYOK tests
└── specs/001-hackpilot/          # Spec Kit artifacts
```

★ = new file added in this enhancement round.

---

## Development

```bash
# Format
black .

# Lint
ruff check . --fix

# Type check
mypy .

# Test
pytest -v
```

All four gates must pass before merging.

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Streamlit Cloud instructions.

---

## Tech Stack

- **Frontend:** Streamlit
- **LLM (cloud):** Gemini 2.5 Flash (`google-genai`)
- **LLM (local):** Ollama REST API (`requests`)
- **Languages:** English, Hindi, Marathi
- **Language:** Python 3.11+
- **Deployment:** Streamlit Cloud

---

## License

MIT
