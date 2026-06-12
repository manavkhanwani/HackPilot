"""Feature F3 – Execution Planner."""

from __future__ import annotations

from typing import Any

from hackpilot import ai_provider, prompts
from hackpilot.ai_provider import Provider
from hackpilot.language import Language
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
    *,
    provider: Provider = Provider.GROK,
    ollama_model: str = ai_provider.OLLAMA_DEFAULT_MODELS[0],
    language: Language = Language.ENGLISH,
) -> ExecutionPlan:
    """Return an execution plan for the selected idea."""
    prompt = prompts.execution_planner(idea, feasibility, ctx, language)
    raw: dict[str, Any] = ai_provider.call(
        prompt,
        provider=provider,
        grok_api_key=api_key,
        ollama_model=ollama_model,
        temperature=0.3,
    )
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
