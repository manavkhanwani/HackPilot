"""Unified AI provider layer for HackPilot.

Supports:
  - Gemini (cloud) via google-genai SDK
  - Ollama (local) via its REST API at http://localhost:11434

Resolution order for the Gemini API key:
  1. Caller-supplied ``api_key`` argument (BYOK / sidebar input)
  2. ``st.secrets["GEMINI_API_KEY"]``  (Streamlit Cloud secrets)
  3. Raises ``ConfigurationError``
"""

from __future__ import annotations

import json
import re
from enum import Enum
from typing import Any

import requests


class Provider(str, Enum):
    GEMINI = "Gemini (Cloud)"
    OLLAMA = "Ollama (Local)"


class ConfigurationError(Exception):
    """Raised when required configuration (e.g. API key) is missing."""


OLLAMA_DEFAULT_MODELS: list[str] = [
    "qwen2.5-coder:7b",
    "llama3",
    "mistral",
]

_OLLAMA_BASE_URL = "http://localhost:11434"


# ── helpers ──────────────────────────────────────────────────────────────────


def _extract_json(text: str) -> str:
    """Strip markdown fences if present."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    return match.group(1).strip() if match else text.strip()


def _parse_json(text: str) -> Any:
    """Parse JSON, raising RuntimeError with a truncated preview on failure."""
    cleaned = _extract_json(text)
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            f"AI provider returned non-JSON output: {text[:200]}"
        ) from exc


# ── Gemini ────────────────────────────────────────────────────────────────────


def _resolve_gemini_key(user_key: str | None) -> str:
    """Return a Gemini API key, preferring the user-supplied one."""
    if user_key and user_key.strip():
        return user_key.strip()

    # Lazy import: Streamlit is not available in tests unless mocked.
    try:
        import streamlit as st  # type: ignore[import-untyped]

        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return str(key)
    except Exception:  # pragma: no cover — non-Streamlit environments
        pass

    raise ConfigurationError(
        "No Gemini API key found. "
        "Enter one in the sidebar or add GEMINI_API_KEY to Streamlit secrets."
    )


def _call_gemini(
    api_key: str,
    prompt: str,
    temperature: float,
) -> Any:
    """Call Gemini 2.5 Flash and return parsed JSON."""
    from google import genai  # type: ignore[import-untyped]
    from google.genai import types  # type: ignore[import-untyped]

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(temperature=temperature)

    for attempt in range(2):
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
        text: str = response.text or ""
        try:
            return _parse_json(text)
        except RuntimeError:
            if attempt == 1:
                raise
    raise RuntimeError("Unreachable")  # pragma: no cover


# ── Ollama ────────────────────────────────────────────────────────────────────


def _call_ollama(
    model: str,
    prompt: str,
    temperature: float,
    base_url: str = _OLLAMA_BASE_URL,
) -> Any:
    """Call the Ollama REST API and return parsed JSON."""
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot reach Ollama at {base_url}. "
            "Make sure Ollama is running (`ollama serve`)."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}") from exc

    data = resp.json()
    text: str = data.get("response", "")
    return _parse_json(text)


# ── Public interface ──────────────────────────────────────────────────────────


def call(
    prompt: str,
    *,
    provider: Provider = Provider.GEMINI,
    gemini_api_key: str | None = None,
    ollama_model: str = OLLAMA_DEFAULT_MODELS[0],
    ollama_base_url: str = _OLLAMA_BASE_URL,
    temperature: float = 0.7,
) -> Any:
    """Dispatch a prompt to the selected AI provider and return parsed JSON.

    Args:
        prompt: Full prompt string (system + user combined).
        provider: Which backend to use.
        gemini_api_key: Optional user-supplied Gemini key (BYOK).
            Falls back to ``st.secrets["GEMINI_API_KEY"]`` if omitted.
        ollama_model: Ollama model tag (used only when provider=OLLAMA).
        ollama_base_url: Ollama server URL (default ``http://localhost:11434``).
        temperature: Sampling temperature forwarded to the model.

    Returns:
        Parsed JSON value (dict or list).

    Raises:
        ConfigurationError: When the Gemini key cannot be resolved.
        RuntimeError: On API / network / JSON-parse failures.
    """
    if provider is Provider.GEMINI:
        key = _resolve_gemini_key(gemini_api_key)
        return _call_gemini(key, prompt, temperature)

    if provider is Provider.OLLAMA:
        return _call_ollama(ollama_model, prompt, temperature, ollama_base_url)

    raise ValueError(f"Unknown provider: {provider}")  # pragma: no cover
