"""Feature F1 – Idea Generator."""

from __future__ import annotations

from typing import Any

from hackpilot import ai_provider, prompts
from hackpilot.ai_provider import Provider
from hackpilot.language import Language
from hackpilot.models import HackathonContext, ProjectIdea


def generate_ideas(
    ctx: HackathonContext,
    api_key: str,
    *,
    provider: Provider = Provider.GEMINI,
    ollama_model: str = ai_provider.OLLAMA_DEFAULT_MODELS[0],
    language: Language = Language.ENGLISH,
) -> list[ProjectIdea]:
    """Return project ideas for the given hackathon context."""
    prompt = prompts.idea_generator(ctx, language)
    raw: list[Any] = ai_provider.call(
        prompt,
        provider=provider,
        gemini_api_key=api_key,
        ollama_model=ollama_model,
        temperature=0.7,
    )

    ideas: list[ProjectIdea] = []
    for item in raw:
        diff = item.get("difficulty", "Medium")
        if diff not in ("Easy", "Medium", "Hard"):
            diff = "Medium"
        ideas.append(
            ProjectIdea(
                title=str(item["title"]),
                problem_statement=str(item["problem_statement"]),
                solution_summary=str(item["solution_summary"]),
                innovation_score=int(item.get("innovation_score", 5)),
                difficulty=diff,
            )
        )
    return ideas
