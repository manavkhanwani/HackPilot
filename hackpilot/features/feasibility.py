"""Feature F2 – Feasibility Analyzer."""

from __future__ import annotations

from typing import Any

from hackpilot import gemini, prompts
from hackpilot.models import FeasibilityReport, HackathonContext, ProjectIdea


def analyze_feasibility(
    idea: ProjectIdea, ctx: HackathonContext, api_key: str
) -> FeasibilityReport:
    """Return a feasibility report for the selected idea."""
    prompt = prompts.feasibility_analyzer(idea, ctx)
    raw: dict[str, Any] = gemini.call(api_key, prompt, temperature=0.3)
    return FeasibilityReport(
        is_feasible=bool(raw.get("is_feasible", True)),
        confidence=int(raw.get("confidence", 5)),
        risks=list(raw.get("risks", [])),
        recommendations=list(raw.get("recommendations", [])),
    )
