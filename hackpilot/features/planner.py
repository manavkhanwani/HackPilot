"""Feature F3 – Execution Planner."""

from __future__ import annotations

from typing import Any

from hackpilot import gemini, prompts
from hackpilot.models import (
    ExecutionPlan,
    FeasibilityReport,
    HackathonContext,
    Milestone,
    ProjectIdea,
)


def build_plan(
    idea: ProjectIdea,
    feasibility: FeasibilityReport,
    ctx: HackathonContext,
    api_key: str,
) -> ExecutionPlan:
    """Return an execution plan for the selected idea."""
    prompt = prompts.execution_planner(idea, feasibility, ctx)
    raw: dict[str, Any] = gemini.call(api_key, prompt, temperature=0.3)
    milestones = [
        Milestone(
            title=str(m["title"]),
            description=str(m["description"]),
            time_offset_hours=int(m.get("time_offset_hours", 0)),
        )
        for m in raw.get("milestones", [])
    ]
    return ExecutionPlan(
        mvp_scope=list(raw.get("mvp_scope", [])),
        stretch_goals=list(raw.get("stretch_goals", [])),
        milestones=milestones,
    )
