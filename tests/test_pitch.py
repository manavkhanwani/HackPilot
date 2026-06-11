"""Tests for F4 – Elevator Pitch Generator."""

from __future__ import annotations

from unittest.mock import patch

from hackpilot.features.pitch import generate_pitch
from hackpilot.models import ElevatorPitch, ExecutionPlan, Milestone, ProjectIdea

IDEA = ProjectIdea(
    title="QuizBot",
    problem_statement="Students lack quick self-assessment tools.",
    solution_summary="AI quiz generator from lecture notes.",
    innovation_score=8,
    difficulty="Medium",
)
PLAN = ExecutionPlan(
    mvp_scope=["Upload notes", "Generate quiz", "Show score"],
    stretch_goals=["Leaderboard"],
    milestones=[Milestone("Core", "Upload + parse", 4)],
)
MOCK = {
    "tagline": "Turn notes into knowledge instantly.",
    "pitch_text": "QuizBot transforms your notes into a personalised quiz in seconds.",
}


def test_returns_elevator_pitch() -> None:
    with patch("hackpilot.features.pitch.gemini.call", return_value=MOCK):
        pitch = generate_pitch(IDEA, PLAN, "fake")
    assert isinstance(pitch, ElevatorPitch)
    assert "QuizBot" in pitch.pitch_text
    assert len(pitch.tagline) > 0


def test_empty_response_gives_empty_strings() -> None:
    with patch("hackpilot.features.pitch.gemini.call", return_value={}):
        pitch = generate_pitch(IDEA, PLAN, "fake")
    assert pitch.tagline == ""
    assert pitch.pitch_text == ""
