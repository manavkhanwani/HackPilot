"""Feature F5 – README Generator."""

from __future__ import annotations

from typing import Any

from hackpilot import ai_provider, prompts
from hackpilot.ai_provider import Provider
from hackpilot.language import Language
from hackpilot.models import ExecutionPlan, HackathonContext, ProjectIdea, ReadmeDraft


def generate_readme(
    idea: ProjectIdea,
    plan: ExecutionPlan,
    ctx: HackathonContext,
    api_key: str,
    *,
    provider: Provider = Provider.GROK,
    ollama_model: str = ai_provider.OLLAMA_DEFAULT_MODELS[0],
    language: Language = Language.ENGLISH,
) -> ReadmeDraft:
    """Return a GitHub README draft as markdown."""
    prompt = prompts.readme_generator(idea, plan, ctx, language)
    raw: dict[str, Any] = ai_provider.call(
        prompt,
        provider=provider,
        grok_api_key=api_key,
        ollama_model=ollama_model,
        temperature=0.5,
    )
    return ReadmeDraft(markdown=str(raw.get("markdown", "")))
