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
- [x] Implement `hackpilot/GROK.py`
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

---

## Phase 7 – Indian Language Support (F6)
- [x] Create `hackpilot/language.py` (`Language` enum, instruction builders)
- [x] Update `hackpilot/prompts.py` — add `language` param to all 5 builders
- [x] Update `hackpilot/features/idea_generator.py` — thread `language`
- [x] Update `hackpilot/features/feasibility.py` — thread `language`
- [x] Update `hackpilot/features/planner.py` — thread `language`
- [x] Update `hackpilot/features/pitch.py` — thread `language`
- [x] Update `hackpilot/features/readme_gen.py` — thread `language`
- [x] Add language selector to `app.py` sidebar
- [x] Wire `language` through `_ai_kwargs` in `app.py`
- [x] Write language tests in `tests/test_enhancements.py`
- [x] Update `specs/001-hackpilot/spec.md` (F6)
- [x] Update `README.md` (language section)

## Phase 8 – Local AI Inference / Ollama (F7)
- [x] Create `hackpilot/ai_provider.py` (`Provider` enum, `call()` dispatcher)
- [x] Implement `_call_ollama()` using `requests` + Ollama REST API
- [x] Implement `_call_GROK()` (extracted from old `GROK.py`)
- [x] Update all 5 feature modules to call `ai_provider.call()`
- [x] Add provider + model selectors to `app.py` sidebar
- [x] Add `requests>=2.31.0` to `requirements.txt`
- [x] Write provider tests in `tests/test_enhancements.py`
- [x] Update `specs/001-hackpilot/spec.md` (F7)
- [x] Update `README.md` (Ollama section)

## Phase 9 – BYOK / GROK API Key (F8)
- [x] Implement `_resolve_GROK_key()` with 3-level resolution in `ai_provider.py`
- [x] Add `ConfigurationError` class
- [x] Add password field to `app.py` sidebar
- [x] Replace all `st.secrets["GROK_API_KEY"]` reads in `app.py` with `_ai_kwargs`
- [x] Add `_handle_config_error()` helper in `app.py`
- [x] Write BYOK key-resolution tests in `tests/test_enhancements.py`
- [x] Update `specs/001-hackpilot/spec.md` (F8)
- [x] Update `README.md` (BYOK section)

## Phase 10 – QA Gates (post-enhancement)
- [ ] Run and confirm: `black .`
- [ ] Run and confirm: `ruff check .`
- [ ] Run and confirm: `mypy .`
- [ ] Run and confirm: `pytest`
