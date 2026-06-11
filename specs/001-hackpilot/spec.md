# Spec – 001-hackpilot

## Overview
HackPilot guides a student through the lifecycle of a hackathon: from receiving a theme to having a polished pitch and README draft ready to share.

## User Journey
1. User selects an output language (English, Hindi, Marathi) and AI provider (Gemini or Ollama) in the sidebar.
2. User enters hackathon context (theme, team size, duration, preferred tech).
3. HackPilot generates 3–5 project ideas with problem statements, solution summaries, innovation scores, and difficulty levels — in the selected language.
4. User selects one idea.
5. HackPilot runs a feasibility analysis against the available time and team size.
6. HackPilot generates an execution plan with milestones, MVP scope, and stretch goals.
7. HackPilot generates an elevator pitch (≤ 60 seconds spoken).
8. HackPilot generates a GitHub README draft.

## Features

### F1 – Idea Generator
**Inputs:** theme (str), team_size (int 1–5), duration_hours (int), preferred_tech (list[str])  
**Outputs:** list of `ProjectIdea` (3–5 items)  
- `title`: str  
- `problem_statement`: str  
- `solution_summary`: str  
- `innovation_score`: int (1–10)  
- `difficulty`: Literal["Easy", "Medium", "Hard"]

### F2 – Feasibility Analyzer
**Inputs:** selected `ProjectIdea`, team_size, duration_hours  
**Outputs:** `FeasibilityReport`  
- `is_feasible`: bool  
- `confidence`: int (1–10)  
- `risks`: list[str]  
- `recommendations`: list[str]

### F3 – Execution Planner
**Inputs:** selected `ProjectIdea`, `FeasibilityReport`, team_size, duration_hours  
**Outputs:** `ExecutionPlan`  
- `mvp_scope`: list[str]  
- `stretch_goals`: list[str]  
- `milestones`: list[`Milestone`]  
  - `Milestone`: `{title, description, time_offset_hours}`

### F4 – Elevator Pitch Generator
**Inputs:** selected `ProjectIdea`, `ExecutionPlan`  
**Outputs:** `ElevatorPitch`  
- `pitch_text`: str (≤ 150 words)  
- `tagline`: str (≤ 10 words)

### F5 – README Generator
**Inputs:** selected `ProjectIdea`, `ExecutionPlan`, team_size, preferred_tech  
**Outputs:** `ReadmeDraft`  
- `markdown`: str

### F6 – Indian Language Support
**Inputs:** language selector (sidebar)  
**Options:** English, Hindi (हिन्दी), Marathi (मराठी)  
**Behaviour:**  
- Selected language is passed to every prompt builder.  
- Gemini's native multilingual capability is used — no external translation APIs.  
- A language-enforcement instruction is prepended to each prompt so the model responds exclusively in the selected language.  
- JSON keys remain in English to ensure deterministic parsing; only human-readable string values are translated.  
- Language selection is global: changing it clears all downstream session state (ideas, feasibility, plan, pitch, readme).

### F7 – Local AI Inference (Ollama)
**Inputs:** provider selector (sidebar), model selector (sidebar)  
**Options:**  
- Gemini (Cloud) — default  
- Ollama (Local) — calls `http://localhost:11434/api/generate`  
**Supported default models:** `qwen2.5-coder:7b`, `llama3`, `mistral`  
**Behaviour:**  
- Implemented in `hackpilot/ai_provider.py`; all features call `ai_provider.call()` rather than `gemini.call()` directly.  
- Custom model tags can be entered as free text.  
- A clear error is shown if Ollama is unreachable.

### F8 – Bring Your Own Key (BYOK)
**Inputs:** password field in sidebar ("Gemini API Key")  
**Resolution order:**  
1. User-supplied key (sidebar password field)  
2. `st.secrets["GEMINI_API_KEY"]` (Streamlit Cloud secrets)  
3. `ConfigurationError` displayed to the user  
**Behaviour:**  
- Keys are never logged or echoed.  
- The field is rendered with `type="password"`.  
- BYOK only applies to the Gemini provider; Ollama requires no key.

## UI Structure (Streamlit)
- Sidebar — top to bottom:
  - **Language selector** (🌐 Language) — output language.
  - **AI Provider selector** (🤖 AI Provider) — Gemini or Ollama.
    - Gemini: optional BYOK key field.
    - Ollama: model selector + custom model field.
  - **Hackathon Context** inputs (theme, team size, duration, tech).
- Tab 1 – **Ideas**: run Idea Generator, display cards, select idea.
- Tab 2 – **Feasibility**: run Feasibility Analyzer on selected idea.
- Tab 3 – **Plan**: run Execution Planner.
- Tab 4 – **Pitch**: run Elevator Pitch Generator.
- Tab 5 – **README**: run README Generator with copy button.

## AI Service Layer
```
hackpilot/ai_provider.py   ← single call() entry point
    Provider.GEMINI  → google-genai SDK → Gemini 2.5 Flash
    Provider.OLLAMA  → requests POST  → localhost:11434/api/generate
```
`hackpilot/gemini.py` is **retained** for backward compatibility but is no longer called by application code.

## Error Handling
- Gemini API errors: user-friendly message + retry button.
- Ollama unreachable: clear message with `ollama serve` hint.
- Missing API key: `ConfigurationError` with actionable instructions.
- Missing inputs: inline Streamlit warnings before LLM call.

## Out of Scope (MVP)
- Saving/exporting results as files.
- Multiple simultaneous sessions.
- Streaming responses.
- Additional languages beyond English, Hindi, Marathi.
