"""Feature F4 – Elevator Pitch Generator."""

from __future__ import annotations

from typing import Any

from hackpilot import gemini, prompts
from hackpilot.models import ElevatorPitch, ExecutionPlan, ProjectIdea


def generate_pitch(
    idea: ProjectIdea, plan: ExecutionPlan, api_key: str
) -> ElevatorPitch:
    """Return an elevator pitch for the selected idea and plan."""
    prompt = prompts.elevator_pitch(idea, plan)
    raw: dict[str, Any] = gemini.call(api_key, prompt, temperature=0.7)
    return ElevatorPitch(
        tagline=str(raw.get("tagline", "")),
        pitch_text=str(raw.get("pitch_text", "")),
    )
