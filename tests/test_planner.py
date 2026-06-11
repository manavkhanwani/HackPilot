"""Tests for F3 – Execution Planner."""

from __future__ import annotations

from unittest.mock import patch

from hackpilot.features.planner import build_plan
from hackpilot.models import (
    ExecutionPlan,
    FeasibilityReport,
    HackathonContext,
    ProjectIdea,
)

CTX = HackathonContext(theme="EdTech", team_size=3, duration_hours=36)
IDEA = ProjectIdea(
    title="QuizBot",
    problem_statement="Students lack quick self-assessment tools.",
    solution_summary="AI quiz generator from lecture notes.",
    innovation_score=8,
    difficulty="Medium",
)
FEASIBILITY = FeasibilityReport(
    is_feasible=True,
    confidence=7,
    risks=["LLM latency"],
    recommendations=["Cache quiz results"],
)
MOCK = {
    "mvp_scope": ["Upload notes", "Generate quiz", "Show score"],
    "stretch_goals": ["Leaderboard", "Export PDF"],
    "milestones": [
        {
            "title": "Core upload",
            "description": "File upload + parse",
            "time_offset_hours": 4,
        },
        {
            "title": "Quiz engine",
            "description": "Gemini-powered Q&A",
            "time_offset_hours": 12,
        },
    ],
}


def test_returns_execution_plan() -> None:
    with patch("hackpilot.features.planner.gemini.call", return_value=MOCK):
        plan = build_plan(IDEA, FEASIBILITY, CTX, "fake")
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.mvp_scope) == 3
    assert len(plan.milestones) == 2
    assert plan.milestones[0].time_offset_hours == 4


def test_empty_response_gives_empty_plan() -> None:
    with patch("hackpilot.features.planner.gemini.call", return_value={}):
        plan = build_plan(IDEA, FEASIBILITY, CTX, "fake")
    assert plan.mvp_scope == []
    assert plan.milestones == []
