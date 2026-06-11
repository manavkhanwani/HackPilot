# Research – 001-hackpilot

## LLM Choice: Gemini 2.5 Flash
- **Why Flash over Pro:** Lower latency, sufficient quality for structured generation, free tier suitable for hackathon demo.
- **SDK:** `google-generativeai` (Python). Key loaded from `st.secrets["GEMINI_API_KEY"]`.
- **Structured output strategy:** Prompt instructs model to return JSON matching a defined schema; response parsed with `json.loads`. Fallback: retry once on parse failure.
- **Context window:** 1M tokens – no chunking needed for MVP inputs.

## Prompt Engineering Approach
- System instruction sets role: "You are HackPilot, a hackathon strategy assistant."
- Each feature has an isolated prompt builder function in `hackpilot/prompts.py`.
- Output format specified inline in prompt with JSON schema example.
- Temperature: 0.7 for ideation; 0.3 for feasibility and planning (determinism preferred).

## Streamlit Specifics
- `st.session_state` used to persist: selected idea, feasibility report, execution plan across tabs.
- `st.secrets` used exclusively for API key – no `.env` file at runtime.
- `st.spinner` wraps all LLM calls.
- Tabs via `st.tabs()`.

## Deployment: Streamlit Cloud
- Repo pushed to GitHub; connected via Streamlit Cloud dashboard.
- `GEMINI_API_KEY` added as a Streamlit Cloud secret.
- No Docker or CI needed for MVP demo.

## Quality Tools
| Tool | Role | Config file |
|------|------|-------------|
| Black | Formatter | `pyproject.toml` |
| Ruff | Linter | `pyproject.toml` |
| MyPy | Type checker | `pyproject.toml` |
| Pytest | Unit tests | `pyproject.toml` |

## Risks
1. **Gemini JSON parse failures** – mitigated by retry logic and lenient parsing.
2. **Rate limits on free tier** – acceptable for demo; add sleep if needed.
3. **Session state loss on rerun** – standard Streamlit behaviour; user must re-enter context only once per session.
