"""HackPilot Pipeline – runs all five features sequentially with gate checks."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from hackpilot.ai_provider import Provider
from hackpilot.features.feasibility import analyze_feasibility
from hackpilot.features.idea_generator import generate_ideas
from hackpilot.features.pitch import generate_pitch
from hackpilot.features.planner import build_plan
from hackpilot.features.readme_gen import generate_readme
from hackpilot.language import Language
from hackpilot.models import (
    ElevatorPitch,
    ExecutionPlan,
    FeasibilityReport,
    HackathonContext,
    ProjectIdea,
    ReadmeDraft,
)


# ── Gate / check results ──────────────────────────────────────────────────────

@dataclass
class GateResult:
    name: str
    passed: bool
    message: str
    detail: str = ""


@dataclass
class StepResult:
    step_name: str
    success: bool
    elapsed_s: float
    output: Any = None
    error: str = ""
    gates: list[GateResult] = field(default_factory=list)

    @property
    def gates_passed(self) -> int:
        return sum(1 for g in self.gates if g.passed)

    @property
    def all_gates_passed(self) -> bool:
        return all(g.passed for g in self.gates)


@dataclass
class PipelineResult:
    steps: list[StepResult] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return all(s.success and s.all_gates_passed for s in self.steps)

    @property
    def final_idea(self) -> ProjectIdea | None:
        for s in self.steps:
            if s.step_name == "Idea Generator" and s.output:
                return s.output[0] if isinstance(s.output, list) else s.output
        return None

    @property
    def final_feasibility(self) -> FeasibilityReport | None:
        for s in self.steps:
            if s.step_name == "Feasibility Analyzer":
                return s.output
        return None

    @property
    def final_plan(self) -> ExecutionPlan | None:
        for s in self.steps:
            if s.step_name == "Execution Planner":
                return s.output
        return None

    @property
    def final_pitch(self) -> ElevatorPitch | None:
        for s in self.steps:
            if s.step_name == "Elevator Pitch":
                return s.output
        return None

    @property
    def final_readme(self) -> ReadmeDraft | None:
        for s in self.steps:
            if s.step_name == "README Generator":
                return s.output
        return None


# ── Gate definitions (5 gates total, one per pipeline step) ──────────────────

def _gate_ideas(ideas: list[ProjectIdea]) -> GateResult:
    """Gate 1 – at least one valid idea with a non-empty title and innovation ≥ 1."""
    if not ideas:
        return GateResult("Ideas Non-Empty", False, "No ideas were returned by the AI.")
    bad = [i for i in ideas if not i.title.strip() or i.innovation_score < 1]
    if bad:
        return GateResult(
            "Ideas Non-Empty",
            False,
            f"{len(bad)} idea(s) have a blank title or zero innovation score.",
        )
    return GateResult(
        "Ideas Non-Empty",
        True,
        f"{len(ideas)} idea(s) generated, all with valid titles.",
    )


def _gate_feasibility(report: FeasibilityReport) -> GateResult:
    """Gate 2 – confidence score must be ≥ 3 (too-low = LLM likely hallucinated)."""
    if report.confidence < 3:
        return GateResult(
            "Feasibility Confidence",
            False,
            f"Confidence score {report.confidence}/10 is below threshold (3).",
            detail="Re-run or pick a different idea.",
        )
    return GateResult(
        "Feasibility Confidence",
        True,
        f"Confidence score {report.confidence}/10 ✓",
    )


def _gate_plan(plan: ExecutionPlan) -> GateResult:
    """Gate 3 – plan must have ≥ 1 MVP feature and ≥ 1 milestone."""
    issues: list[str] = []
    if not plan.mvp_scope:
        issues.append("MVP scope is empty")
    if not plan.milestones:
        issues.append("No milestones defined")
    if issues:
        return GateResult("Plan Completeness", False, "; ".join(issues) + ".")
    return GateResult(
        "Plan Completeness",
        True,
        f"{len(plan.mvp_scope)} MVP feature(s), {len(plan.milestones)} milestone(s) ✓",
    )


def _gate_pitch(pitch: ElevatorPitch) -> GateResult:
    """Gate 4 – pitch text must be at least 50 characters (non-trivial output)."""
    min_len = 50
    txt_len = len(pitch.pitch_text.strip())
    if txt_len < min_len:
        return GateResult(
            "Pitch Length",
            False,
            f"Pitch text is only {txt_len} chars (minimum {min_len}).",
        )
    return GateResult(
        "Pitch Length",
        True,
        f"Pitch text length {txt_len} chars ✓",
    )


def _gate_readme(readme: ReadmeDraft) -> GateResult:
    """Gate 5 – README markdown must contain at least one heading (#)."""
    if "#" not in readme.markdown:
        return GateResult(
            "README Structure",
            False,
            "README contains no markdown headings — likely malformed output.",
        )
    heading_count = readme.markdown.count("\n#")
    return GateResult(
        "README Structure",
        True,
        f"README has {heading_count + 1} section(s) ✓",
    )


# ── Pipeline runner ───────────────────────────────────────────────────────────

def run_pipeline(
    ctx: HackathonContext,
    *,
    provider: Provider,
    gemini_api_key: str,
    ollama_model: str,
    language: Language,
) -> PipelineResult:
    """
    Execute all five HackPilot features in sequence.
    Each step has a dedicated gate check; a gate failure stops the pipeline.
    """
    result = PipelineResult()
    ai_kw = dict(
        provider=provider,
        gemini_api_key=gemini_api_key,
        ollama_model=ollama_model,
        language=language,
    )

    # ── Step 1: Idea Generator ────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        ideas = generate_ideas(ctx, api_key=gemini_api_key, **ai_kw)
        gate = _gate_ideas(ideas)
        step = StepResult(
            step_name="Idea Generator",
            success=True,
            elapsed_s=time.perf_counter() - t0,
            output=ideas,
            gates=[gate],
        )
    except Exception as exc:
        step = StepResult(
            step_name="Idea Generator",
            success=False,
            elapsed_s=time.perf_counter() - t0,
            error=str(exc),
        )
    result.steps.append(step)
    if not step.success or not step.all_gates_passed:
        return result  # hard stop

    best_idea: ProjectIdea = ideas[0]  # highest-ranked idea from LLM

    # ── Step 2: Feasibility Analyzer ─────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        feasibility = analyze_feasibility(best_idea, ctx, api_key=gemini_api_key, **ai_kw)
        gate = _gate_feasibility(feasibility)
        step = StepResult(
            step_name="Feasibility Analyzer",
            success=True,
            elapsed_s=time.perf_counter() - t0,
            output=feasibility,
            gates=[gate],
        )
    except Exception as exc:
        step = StepResult(
            step_name="Feasibility Analyzer",
            success=False,
            elapsed_s=time.perf_counter() - t0,
            error=str(exc),
        )
    result.steps.append(step)
    if not step.success or not step.all_gates_passed:
        return result

    # ── Step 3: Execution Planner ─────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        plan = build_plan(best_idea, feasibility, ctx, api_key=gemini_api_key, **ai_kw)
        gate = _gate_plan(plan)
        step = StepResult(
            step_name="Execution Planner",
            success=True,
            elapsed_s=time.perf_counter() - t0,
            output=plan,
            gates=[gate],
        )
    except Exception as exc:
        step = StepResult(
            step_name="Execution Planner",
            success=False,
            elapsed_s=time.perf_counter() - t0,
            error=str(exc),
        )
    result.steps.append(step)
    if not step.success or not step.all_gates_passed:
        return result

    # ── Step 4: Elevator Pitch ────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        pitch = generate_pitch(best_idea, plan, api_key=gemini_api_key, **ai_kw)
        gate = _gate_pitch(pitch)
        step = StepResult(
            step_name="Elevator Pitch",
            success=True,
            elapsed_s=time.perf_counter() - t0,
            output=pitch,
            gates=[gate],
        )
    except Exception as exc:
        step = StepResult(
            step_name="Elevator Pitch",
            success=False,
            elapsed_s=time.perf_counter() - t0,
            error=str(exc),
        )
    result.steps.append(step)
    if not step.success or not step.all_gates_passed:
        return result

    # ── Step 5: README Generator ──────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        readme = generate_readme(best_idea, plan, ctx, api_key=gemini_api_key, **ai_kw)
        gate = _gate_readme(readme)
        step = StepResult(
            step_name="README Generator",
            success=True,
            elapsed_s=time.perf_counter() - t0,
            output=readme,
            gates=[gate],
        )
    except Exception as exc:
        step = StepResult(
            step_name="README Generator",
            success=False,
            elapsed_s=time.perf_counter() - t0,
            error=str(exc),
        )
    result.steps.append(step)

    return result
