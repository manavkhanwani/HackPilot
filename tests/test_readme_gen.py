"""Tests for F5 – README Generator."""

from __future__ import annotations

from unittest.mock import patch

from hackpilot.features.readme_gen import generate_readme
from hackpilot.models import (
    ExecutionPlan,
    HackathonContext,
    Milestone,
    ProjectIdea,
    ReadmeDraft,
)

CTX = HackathonContext(
    theme="EdTech",
    team_size=2,
    duration_hours=24,
    preferred_tech=["Python", "Streamlit"],
)
IDEA = ProjectIdea(
    title="QuizBot",
    problem_statement="Students lack quick self-assessment tools.",
    solution_summary="AI quiz generator from lecture notes.",
    innovation_score=8,
    difficulty="Medium",
)
PLAN = ExecutionPlan(
    mvp_scope=["Upload notes", "Generate quiz"],
    stretch_goals=["Leaderboard"],
    milestones=[Milestone("Core", "Upload + parse", 4)],
)
MOCK = {"markdown": "# QuizBot\n\nAI-powered quiz generator."}


def test_returns_readme_draft() -> None:
    with patch("hackpilot.features.readme_gen.gemini.call", return_value=MOCK):
        draft = generate_readme(IDEA, PLAN, CTX, "fake")
    assert isinstance(draft, ReadmeDraft)
    assert "QuizBot" in draft.markdown


def test_empty_response_gives_empty_markdown() -> None:
    with patch("hackpilot.features.readme_gen.gemini.call", return_value={}):
        draft = generate_readme(IDEA, PLAN, CTX, "fake")
    assert draft.markdown == ""
