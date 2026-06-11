# Data Model – 001-hackpilot

All models are Python `dataclasses` (or `TypedDict` for JSON interchange). No database. Stored in `st.session_state` during a session.

---

## HackathonContext
```python
@dataclass
class HackathonContext:
    theme: str
    team_size: int          # 1–5
    duration_hours: int     # e.g. 24, 36, 48
    preferred_tech: list[str]
```

---

## ProjectIdea
```python
@dataclass
class ProjectIdea:
    title: str
    problem_statement: str
    solution_summary: str
    innovation_score: int   # 1–10
    difficulty: str         # "Easy" | "Medium" | "Hard"
```

---

## FeasibilityReport
```python
@dataclass
class FeasibilityReport:
    is_feasible: bool
    confidence: int         # 1–10
    risks: list[str]
    recommendations: list[str]
```

---

## Milestone
```python
@dataclass
class Milestone:
    title: str
    description: str
    time_offset_hours: int  # hours from hackathon start
```

## ExecutionPlan
```python
@dataclass
class ExecutionPlan:
    mvp_scope: list[str]
    stretch_goals: list[str]
    milestones: list[Milestone]
```

---

## ElevatorPitch
```python
@dataclass
class ElevatorPitch:
    tagline: str            # ≤ 10 words
    pitch_text: str         # ≤ 150 words
```

---

## ReadmeDraft
```python
@dataclass
class ReadmeDraft:
    markdown: str
```

---

## Session State Keys
| Key | Type | Set by |
|-----|------|--------|
| `context` | `HackathonContext` | Sidebar inputs |
| `ideas` | `list[ProjectIdea]` | F1 |
| `selected_idea` | `ProjectIdea` | Tab 1 selection |
| `feasibility` | `FeasibilityReport` | F2 |
| `plan` | `ExecutionPlan` | F3 |
| `pitch` | `ElevatorPitch` | F4 |
| `readme` | `ReadmeDraft` | F5 |
