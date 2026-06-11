# 🚀 HackPilot

> **AI-powered hackathon copilot for students.**  
> Go from theme to pitch in minutes — with Gemini 2.5 Flash doing the heavy lifting.

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

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/your-org/hackpilot.git
cd hackpilot
pip install -r requirements.txt
```

### 2. Add your Gemini API key

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and set GEMINI_API_KEY
```

Get a free key at <https://aistudio.google.com/app/apikey>.

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
│   ├── gemini.py                 # google-genai API wrapper
│   ├── prompts.py                # Prompt builders for all 5 features
│   └── features/
│       ├── idea_generator.py     # F1
│       ├── feasibility.py        # F2
│       ├── planner.py            # F3
│       ├── pitch.py              # F4
│       └── readme_gen.py         # F5
├── tests/                        # Pytest unit tests (11 tests)
└── specs/001-hackpilot/          # Spec Kit artifacts
```

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
- **LLM:** Gemini 2.5 Flash (`google-genai`)
- **Language:** Python 3.11+
- **Deployment:** Streamlit Cloud

---

## License

MIT
