"""Unit tests for all 5 HackPilot pipeline gate checks."""

from __future__ import annotations

import pytest

from hackpilot.models import (
    ElevatorPitch,
    ExecutionPlan,
    FeasibilityReport,
    Milestone,
    ProjectIdea,
    ReadmeDraft,
)
from hackpilot.pipeline import (
    _gate_feasibility,
    _gate_ideas,
    _gate_pitch,
    _gate_plan,
    _gate_readme,
)


# ── Gate 1: Ideas Non-Empty ───────────────────────────────────────────────────

class TestGateIdeas:
    def _idea(self, title="Test Idea", score=7) -> ProjectIdea:
        return ProjectIdea(
            title=title,
            problem_statement="Some problem",
            solution_summary="Some solution",
            innovation_score=score,
            difficulty="Medium",
        )

    def test_passes_with_valid_ideas(self):
        result = _gate_ideas([self._idea()])
        assert result.passed

    def test_fails_on_empty_list(self):
        result = _gate_ideas([])
        assert not result.passed
        assert "No ideas" in result.message

    def test_fails_on_blank_title(self):
        result = _gate_ideas([self._idea(title="   ")])
        assert not result.passed

    def test_fails_on_zero_innovation_score(self):
        result = _gate_ideas([self._idea(score=0)])
        assert not result.passed

    def test_passes_with_multiple_ideas(self):
        result = _gate_ideas([self._idea(), self._idea("Idea 2")])
        assert result.passed


# ── Gate 2: Feasibility Confidence ───────────────────────────────────────────

class TestGateFeasibility:
    def _report(self, confidence: int) -> FeasibilityReport:
        return FeasibilityReport(
            is_feasible=True,
            confidence=confidence,
            risks=[],
            recommendations=[],
        )

    def test_passes_at_threshold(self):
        assert _gate_feasibility(self._report(3)).passed

    def test_passes_above_threshold(self):
        assert _gate_feasibility(self._report(9)).passed

    def test_fails_below_threshold(self):
        result = _gate_feasibility(self._report(2))
        assert not result.passed
        assert "2" in result.message

    def test_fails_at_zero(self):
        assert not _gate_feasibility(self._report(0)).passed

    def test_passes_at_max(self):
        assert _gate_feasibility(self._report(10)).passed


# ── Gate 3: Plan Completeness ─────────────────────────────────────────────────

class TestGatePlan:
    def _milestone(self) -> Milestone:
        return Milestone(title="Launch", description="Ship MVP", time_offset_hours=12)

    def test_passes_with_mvp_and_milestones(self):
        plan = ExecutionPlan(
            mvp_scope=["feature-a"],
            stretch_goals=[],
            milestones=[self._milestone()],
        )
        assert _gate_plan(plan).passed

    def test_fails_with_empty_mvp_scope(self):
        plan = ExecutionPlan(mvp_scope=[], stretch_goals=[], milestones=[self._milestone()])
        result = _gate_plan(plan)
        assert not result.passed
        assert "MVP" in result.message

    def test_fails_with_no_milestones(self):
        plan = ExecutionPlan(mvp_scope=["feature-a"], stretch_goals=[], milestones=[])
        result = _gate_plan(plan)
        assert not result.passed
        assert "milestone" in result.message.lower()

    def test_fails_when_both_empty(self):
        plan = ExecutionPlan(mvp_scope=[], stretch_goals=[], milestones=[])
        assert not _gate_plan(plan).passed

    def test_passes_with_multiple_features_and_milestones(self):
        plan = ExecutionPlan(
            mvp_scope=["f1", "f2", "f3"],
            stretch_goals=["s1"],
            milestones=[self._milestone(), self._milestone()],
        )
        assert _gate_plan(plan).passed


# ── Gate 4: Pitch Length ──────────────────────────────────────────────────────

class TestGatePitch:
    def test_passes_at_exactly_50_chars(self):
        pitch = ElevatorPitch(tagline="tag", pitch_text="A" * 50)
        assert _gate_pitch(pitch).passed

    def test_passes_above_50_chars(self):
        pitch = ElevatorPitch(tagline="tag", pitch_text="A" * 200)
        assert _gate_pitch(pitch).passed

    def test_fails_below_50_chars(self):
        pitch = ElevatorPitch(tagline="tag", pitch_text="too short")
        result = _gate_pitch(pitch)
        assert not result.passed
        assert "9" in result.message  # length reported

    def test_fails_on_empty_pitch(self):
        pitch = ElevatorPitch(tagline="tag", pitch_text="")
        assert not _gate_pitch(pitch).passed

    def test_strips_whitespace_before_checking(self):
        pitch = ElevatorPitch(tagline="t", pitch_text="   " + "A" * 48 + "   ")
        # stripped length = 48 < 50 → should fail
        assert not _gate_pitch(pitch).passed


# ── Gate 5: README Structure ──────────────────────────────────────────────────

class TestGateReadme:
    def test_passes_with_heading(self):
        readme = ReadmeDraft(markdown="# Title\n## Setup\nContent here.")
        assert _gate_readme(readme).passed

    def test_fails_without_any_heading(self):
        readme = ReadmeDraft(markdown="just plain text, no headings at all")
        result = _gate_readme(readme)
        assert not result.passed
        assert "heading" in result.message.lower()

    def test_fails_on_empty_readme(self):
        assert not _gate_readme(ReadmeDraft(markdown="")).passed

    def test_passes_with_inline_heading(self):
        readme = ReadmeDraft(markdown="# HackPilot\nSome content")
        assert _gate_readme(readme).passed

    def test_passes_with_multiple_sections(self):
        md = "# Title\n## Install\n## Usage\n## Contributing"
        assert _gate_readme(ReadmeDraft(markdown=md)).passed
