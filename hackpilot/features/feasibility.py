"""Feature F2 – Feasibility Analyzer."""

from __future__ import annotations

from typing import Any

from hackpilot import ai_provider, prompts
from hackpilot.ai_provider import Provider
from hackpilot.language import Language
from hackpilot.models import FeasibilityReport, HackathonContext, ProjectIdea


def analyze_feasibility(
    idea: ProjectIdea,
    ctx: HackathonContext,
    api_key: str,
    *,
    provider: Provider = Provider.GROK,
    ollama_model: str = ai_provider.OLLAMA_DEFAULT_MODELS[0],
    language: Language = Language.ENGLISH,
) -> FeasibilityReport:
    """Return a feasibility report for the selected idea."""
    prompt = prompts.feasibility_analyzer(idea, ctx, language)
    raw: dict[str, Any] = ai_provider.call(
        prompt,
        provider=provider,
        grok_api_key=api_key,
        ollama_model=ollama_model,
        temperature=0.3,
    )
    return FeasibilityReport(
        is_feasible=bool(raw.get("is_feasible", True)),
        confidence=int(raw.get("confidence", 5)),
        risks=list(raw.get("risks", [])),
        recommendations=list(raw.get("recommendations", [])),
    )
