"""Prompt builders for each HackPilot feature."""

from __future__ import annotations

from hackpilot.models import (
    ExecutionPlan,
    FeasibilityReport,
    HackathonContext,
    ProjectIdea,
)

_SYSTEM = (
    "You are HackPilot, a hackathon strategy assistant for students. "
    "Always respond with valid JSON only — no prose, no markdown fences."
)


def idea_generator(ctx: HackathonContext) -> str:
    tech = ", ".join(ctx.preferred_tech) if ctx.preferred_tech else "any"
    return f"""{_SYSTEM}

Generate exactly 5 hackathon project ideas for the following context:
- Theme: {ctx.theme}
- Team size: {ctx.team_size} person(s)
- Duration: {ctx.duration_hours} hours
- Preferred technologies: {tech}

Return a JSON array of 5 objects with these exact keys:
  "title": string
  "problem_statement": string (1–2 sentences)
  "solution_summary": string (2–3 sentences)
  "innovation_score": integer 1–10
  "difficulty": one of "Easy", "Medium", "Hard"

Calibrate difficulty for a {ctx.team_size}-person team with {ctx.duration_hours} hours.
"""


def feasibility_analyzer(idea: ProjectIdea, ctx: HackathonContext) -> str:
    return f"""{_SYSTEM}

Assess the feasibility of the following hackathon project:
- Title: {idea.title}
- Solution: {idea.solution_summary}
- Team size: {ctx.team_size} person(s)
- Duration: {ctx.duration_hours} hours
- Preferred technologies: {", ".join(ctx.preferred_tech) or "any"}

Return a single JSON object with these exact keys:
  "is_feasible": boolean
  "confidence": integer 1–10
  "risks": array of 3–5 short strings
  "recommendations": array of 3–5 short strings
"""


def execution_planner(
    idea: ProjectIdea,
    feasibility: FeasibilityReport,
    ctx: HackathonContext,
) -> str:
    return f"""{_SYSTEM}

Create an execution plan for this hackathon project:
- Title: {idea.title}
- Solution: {idea.solution_summary}
- Is feasible: {feasibility.is_feasible} (confidence: {feasibility.confidence}/10)
- Team size: {ctx.team_size} person(s)
- Duration: {ctx.duration_hours} hours

Return a single JSON object with these exact keys:
  "mvp_scope": array of 4–6 short feature strings
  "stretch_goals": array of 2–4 short feature strings
  "milestones": array of objects, each with:
      "title": string
      "description": string
      "time_offset_hours": integer (hours from start, within {ctx.duration_hours})
"""


def elevator_pitch(idea: ProjectIdea, plan: ExecutionPlan) -> str:
    mvp = "; ".join(plan.mvp_scope[:3])
    return f"""{_SYSTEM}

Write an elevator pitch for this hackathon project:
- Title: {idea.title}
- Problem: {idea.problem_statement}
- Solution: {idea.solution_summary}
- Key MVP features: {mvp}

Return a single JSON object with these exact keys:
  "tagline": string (max 10 words, punchy)
  "pitch_text": string (max 150 words, suitable for 60-second spoken delivery)
"""


def readme_generator(
    idea: ProjectIdea, plan: ExecutionPlan, ctx: HackathonContext
) -> str:
    tech = ", ".join(ctx.preferred_tech) if ctx.preferred_tech else "TBD"
    mvp = "\n".join(f"- {f}" for f in plan.mvp_scope)
    stretch = "\n".join(f"- {f}" for f in plan.stretch_goals)
    return f"""{_SYSTEM}

Generate a GitHub README in Markdown for this hackathon project:
- Title: {idea.title}
- Problem: {idea.problem_statement}
- Solution: {idea.solution_summary}
- Tech stack: {tech}
- MVP features:
{mvp}
- Stretch goals:
{stretch}

Return a single JSON object with one key:
  "markdown": string (full README markdown, include sections:
      Overview, Problem, Solution, Features, Tech Stack, Getting Started, Team)
"""
