"""Tests for F1 – Idea Generator."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from hackpilot.features.idea_generator import generate_ideas
from hackpilot.models import HackathonContext, ProjectIdea


@pytest.fixture
def ctx() -> HackathonContext:
    return HackathonContext(
        theme="Smart Cities",
        team_size=2,
        duration_hours=24,
        preferred_tech=["Python", "Streamlit"],
    )


MOCK_RESPONSE = [
    {
        "title": "EcoRoute",
        "problem_statement": "Cities lack real-time eco-routing for commuters.",
        "solution_summary": "An app suggesting the greenest route using public data.",
        "innovation_score": 8,
        "difficulty": "Medium",
    }
]


def test_generate_ideas_returns_project_ideas(ctx: HackathonContext) -> None:
    with patch(
        "hackpilot.features.idea_generator.gemini.call", return_value=MOCK_RESPONSE
    ):
        ideas = generate_ideas(ctx, api_key="fake-key")

    assert len(ideas) == 1
    assert isinstance(ideas[0], ProjectIdea)
    assert ideas[0].title == "EcoRoute"
    assert ideas[0].innovation_score == 8
    assert ideas[0].difficulty == "Medium"


def test_generate_ideas_clamps_invalid_difficulty(ctx: HackathonContext) -> None:
    bad_response = [{**MOCK_RESPONSE[0], "difficulty": "Impossible"}]
    with patch(
        "hackpilot.features.idea_generator.gemini.call", return_value=bad_response
    ):
        ideas = generate_ideas(ctx, api_key="fake-key")

    assert ideas[0].difficulty == "Medium"


def test_generate_ideas_propagates_api_error(ctx: HackathonContext) -> None:
    with patch(
        "hackpilot.features.idea_generator.gemini.call",
        side_effect=RuntimeError("API error"),
    ):
        with pytest.raises(RuntimeError, match="API error"):
            generate_ideas(ctx, api_key="fake-key")
