"""Feature F5 – README Generator."""

from __future__ import annotations

from typing import Any

from hackpilot import gemini, prompts
from hackpilot.models import ExecutionPlan, HackathonContext, ProjectIdea, ReadmeDraft


def generate_readme(
    idea: ProjectIdea,
    plan: ExecutionPlan,
    ctx: HackathonContext,
    api_key: str,
) -> ReadmeDraft:
    """Return a GitHub README draft as markdown."""
    prompt = prompts.readme_generator(idea, plan, ctx)
    raw: dict[str, Any] = gemini.call(api_key, prompt, temperature=0.5)
    return ReadmeDraft(markdown=str(raw.get("markdown", "")))
