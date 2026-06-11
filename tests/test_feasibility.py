"""Tests for F2 – Feasibility Analyzer."""

from __future__ import annotations

from unittest.mock import patch

from hackpilot.features.feasibility import analyze_feasibility
from hackpilot.models import FeasibilityReport, HackathonContext, ProjectIdea

CTX = HackathonContext(theme="HealthTech", team_size=2, duration_hours=24)
IDEA = ProjectIdea(
    title="MedRemind",
    problem_statement="Patients forget medication schedules.",
    solution_summary="A smart reminder app with escalation alerts.",
    innovation_score=7,
    difficulty="Easy",
)
MOCK = {
    "is_feasible": True,
    "confidence": 8,
    "risks": ["API rate limits", "SMS cost"],
    "recommendations": ["Use free tier", "Cache aggressively"],
}


def test_returns_feasibility_report() -> None:
    with patch("hackpilot.features.feasibility.gemini.call", return_value=MOCK):
        report = analyze_feasibility(IDEA, CTX, "fake")
    assert isinstance(report, FeasibilityReport)
    assert report.is_feasible is True
    assert report.confidence == 8
    assert len(report.risks) == 2


def test_defaults_on_missing_keys() -> None:
    with patch("hackpilot.features.feasibility.gemini.call", return_value={}):
        report = analyze_feasibility(IDEA, CTX, "fake")
    assert report.is_feasible is True
    assert report.confidence == 5
    assert report.risks == []
