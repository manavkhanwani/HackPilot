# Tasks – 001-hackpilot

## Legend
- `[ ]` Not started
- `[~]` In progress
- `[x]` Done

---

## Phase 1 – Spec Kit Artifacts
- [x] Write `constitution.md`
- [x] Write `specs/001-hackpilot/spec.md`
- [x] Write `specs/001-hackpilot/research.md`
- [x] Write `specs/001-hackpilot/data-model.md`
- [x] Write `specs/001-hackpilot/plan.md`
- [x] Write `specs/001-hackpilot/tasks.md`

## Phase 2 – Scaffolding
- [x] Create `requirements.txt`
- [x] Create `pyproject.toml`
- [x] Create `.gitignore`
- [x] Create placeholder `README.md`
- [x] Create `app.py` (empty Streamlit shell)
- [x] Create `hackpilot/` package skeleton
- [x] Create `tests/` directory
- [x] Create `.streamlit/secrets.toml.example`

## Phase 3 – Idea Generator (F1)
- [x] Implement `hackpilot/models.py`
- [x] Implement `hackpilot/gemini.py`
- [x] Implement `hackpilot/prompts.py` (F1 prompt)
- [x] Implement `hackpilot/features/idea_generator.py`
- [x] Add sidebar context inputs to `app.py`
- [x] Add Tab 1 (Ideas) to `app.py`
- [x] Write `tests/test_idea_generator.py`

## Phase 4 – Feasibility + Planner (F2, F3)
- [x] Implement `hackpilot/features/feasibility.py`
- [x] Add F2 prompt to `hackpilot/prompts.py`
- [x] Add Tab 2 (Feasibility) to `app.py`
- [x] Implement `hackpilot/features/planner.py`
- [x] Add F3 prompt to `hackpilot/prompts.py`
- [x] Add Tab 3 (Plan) to `app.py`
- [x] Write `tests/test_feasibility.py`
- [x] Write `tests/test_planner.py`

## Phase 5 – Pitch + README (F4, F5)
- [x] Implement `hackpilot/features/pitch.py`
- [x] Add F4 prompt to `hackpilot/prompts.py`
- [x] Add Tab 4 (Pitch) to `app.py`
- [x] Implement `hackpilot/features/readme_gen.py`
- [x] Add F5 prompt to `hackpilot/prompts.py`
- [x] Add Tab 5 (README) to `app.py`
- [x] Write `tests/test_pitch.py`
- [x] Write `tests/test_readme_gen.py`

## Phase 6 – Finalization
- [x] Update `README.md` (full documentation)
- [x] Write `DEPLOYMENT.md` (Streamlit Cloud guide)
- [x] Run and confirm: `black .`
- [x] Run and confirm: `ruff check .`
- [x] Run and confirm: `mypy .`
- [x] Run and confirm: `pytest`
- [x] Final `tasks.md` status update
