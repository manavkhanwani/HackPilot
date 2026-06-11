"""Gemini API client wrapper using google-genai SDK."""

from __future__ import annotations

import json
import re
from typing import Any

from google import genai
from google.genai import types


def _extract_json(text: str) -> str:
    """Strip markdown fences if present."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    return match.group(1).strip() if match else text.strip()


def call(api_key: str, prompt: str, temperature: float = 0.7) -> Any:
    """Call Gemini 2.5 Flash and return parsed JSON (dict or list)."""
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(temperature=temperature)

    for attempt in range(2):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        text = response.text or ""
        try:
            return json.loads(_extract_json(text))
        except (json.JSONDecodeError, ValueError):
            if attempt == 1:
                raise RuntimeError(f"Gemini returned non-JSON: {text[:200]}")
    raise RuntimeError("Unreachable")
