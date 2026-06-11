# HackPilot – Constitution

## Purpose
HackPilot is an AI-powered copilot for students participating in hackathons solo or in small teams. It reduces the cognitive overhead of starting a hackathon by automating ideation, feasibility checking, planning, and pitch generation.

## Guiding Principles
1. **Simplicity first** – every screen should do one thing well.
2. **Speed over polish** – outputs must be useful within seconds.
3. **Student-centric** – language, scope, and assumptions target undergraduate-level hackathon participants.
4. **LLM-transparent** – AI outputs are clearly labelled; users can regenerate at any time.

## Non-Goals (MVP)
- No user accounts or persistence.
- No team collaboration features.
- No real-time data (trends, APIs for prize tracks, etc.).
- No fine-tuning or RAG.

## Technology Constraints
- Frontend: Streamlit only.
- LLM: Google Gemini 2.5 Flash via `google-generativeai` SDK.
- Language: Python 3.11+.
- Deployment: Streamlit Cloud.
- Storage: None (session state only).

## Quality Gates
All PRs must pass:
```
black .
ruff check .
mypy .
pytest
```
