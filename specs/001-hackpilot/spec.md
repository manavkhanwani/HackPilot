# Spec – 001-hackpilot

## Overview
HackPilot guides a student through the lifecycle of a hackathon: from receiving a theme to having a polished pitch and README draft ready to share.

## User Journey
1. User enters hackathon context (theme, team size, duration, preferred tech).
2. HackPilot generates 3–5 project ideas with problem statements, solution summaries, innovation scores, and difficulty levels.
3. User selects one idea.
4. HackPilot runs a feasibility analysis against the available time and team size.
5. HackPilot generates an execution plan with milestones, MVP scope, and stretch goals.
6. HackPilot generates an elevator pitch (≤ 60 seconds spoken).
7. HackPilot generates a GitHub README draft.

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

## UI Structure (Streamlit)
- Sidebar: hackathon context inputs (persistent across tabs).
- Tab 1 – **Ideas**: run Idea Generator, display cards, select idea.
- Tab 2 – **Feasibility**: run Feasibility Analyzer on selected idea.
- Tab 3 – **Plan**: run Execution Planner.
- Tab 4 – **Pitch**: run Elevator Pitch Generator.
- Tab 5 – **README**: run README Generator with copy button.

## Error Handling
- Gemini API errors: display user-friendly message with retry button.
- Missing inputs: inline Streamlit warnings before LLM call.

## Out of Scope (MVP)
- Saving/exporting results as files.
- Multiple simultaneous sessions.
- Streaming responses.
