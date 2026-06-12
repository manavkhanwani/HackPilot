"""Feature F4 – Elevator Pitch Generator."""

from __future__ import annotations

from typing import Any

from hackpilot import ai_provider, prompts
from hackpilot.ai_provider import Provider
from hackpilot.language import Language
from hackpilot.models import ElevatorPitch, ExecutionPlan, ProjectIdea


def generate_pitch(
    idea: ProjectIdea,
    plan: ExecutionPlan,
    api_key: str,
    *,
    provider: Provider = Provider.GEMINI,
    ollama_model: str = ai_provider.OLLAMA_DEFAULT_MODELS[0],
    language: Language = Language.ENGLISH,
) -> ElevatorPitch:
    """Return an elevator pitch for the selected idea and plan."""
    prompt = prompts.elevator_pitch(idea, plan, language)
    raw: dict[str, Any] = ai_provider.call(
        prompt,
        provider=provider,
        grok_api_key=api_key,
        ollama_model=ollama_model,
        temperature=0.7,
    )
    return ElevatorPitch(
        tagline=str(raw.get("tagline", "")),
        pitch_text=str(raw.get("pitch_text", "")),
    )
