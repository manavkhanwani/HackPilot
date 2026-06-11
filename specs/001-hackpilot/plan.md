# Plan – 001-hackpilot

## Phases

### Phase 1 – Spec Kit Artifacts ✅
Deliverables: `constitution.md`, `spec.md`, `research.md`, `data-model.md`, `plan.md`, `tasks.md`

### Phase 2 – Project Scaffolding
Deliverables:
- `requirements.txt`
- `pyproject.toml` (black, ruff, mypy, pytest config)
- `.gitignore`
- `README.md` (placeholder)
- Directory structure:
  ```
  hackpilot/
  ├── app.py
  ├── hackpilot/
  │   ├── __init__.py
  │   ├── models.py
  │   ├── prompts.py
  │   ├── gemini.py
  │   └── features/
  │       ├── __init__.py
  │       ├── idea_generator.py
  │       ├── feasibility.py
  │       ├── planner.py
  │       ├── pitch.py
  │       └── readme_gen.py
  ├── tests/
  │   ├── __init__.py
  │   └── ...
  └── .streamlit/
      └── secrets.toml.example
  ```

### Phase 3 – Feature 1: Idea Generator
- `hackpilot/models.py` – all dataclasses
- `hackpilot/gemini.py` – Gemini client wrapper
- `hackpilot/prompts.py` – prompt builders
- `hackpilot/features/idea_generator.py` – generation logic
- `app.py` – sidebar + Tab 1 UI
- `tests/test_idea_generator.py`

### Phase 4 – Features 2 & 3: Feasibility + Planner
- `hackpilot/features/feasibility.py`
- `hackpilot/features/planner.py`
- Tab 2 & 3 in `app.py`
- Tests

### Phase 5 – Features 4 & 5: Pitch + README
- `hackpilot/features/pitch.py`
- `hackpilot/features/readme_gen.py`
- Tab 4 & 5 in `app.py`
- Tests

### Phase 6 – Finalization
- Final README
- Streamlit Cloud deployment guide
- Quality gate verification

## Constraints
- No parallel feature development – phases are sequential.
- Each phase ends with approval gate.
