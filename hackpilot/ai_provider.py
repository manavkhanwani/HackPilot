"""Unified AI provider layer for HackPilot.

Supports:
  - Grok (cloud) via xAI API (OpenAI-compatible) at https://api.x.ai/v1
  - Ollama (local) via its REST API at http://localhost:11434

Resolution order for the Grok API key:
  1. Caller-supplied ``api_key`` argument (BYOK / sidebar input)
  2. ``st.secrets["GROK_API_KEY"]``  (Streamlit Cloud secrets)
  3. Raises ``ConfigurationError``
"""

from __future__ import annotations

import json
import re
from enum import Enum
from typing import Any

import requests


class Provider(str, Enum):
    GROK = "Grok (xAI Cloud)"
    OLLAMA = "Ollama (Local)"


class ConfigurationError(Exception):
    """Raised when required configuration (e.g. API key) is missing."""


OLLAMA_DEFAULT_MODELS: list[str] = [
    "qwen2.5-coder:7b",
    "llama3",
    "mistral",
]

_OLLAMA_BASE_URL = "http://localhost:11434"
_GROK_BASE_URL = "https://api.x.ai/v1"
_GROK_MODEL = "grok-3"


# ── helpers ───────────────────────────────────────────────────────────────────


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


# ── Grok ──────────────────────────────────────────────────────────────────────


def _resolve_grok_key(user_key: str | None) -> str:
    """Return a Grok API key, preferring the user-supplied one."""
    if user_key and user_key.strip():
        return user_key.strip()

    try:
        import streamlit as st  # type: ignore[import-untyped]

        key = st.secrets.get("GROK_API_KEY", "")
        if key:
            return str(key)
    except Exception:  # pragma: no cover
        pass

    raise ConfigurationError(
        "No Grok API key found. "
        "Enter one in the sidebar or add GROK_API_KEY to Streamlit secrets. "
        "Get your key at https://console.x.ai/"
    )


def _call_grok(
    api_key: str,
    prompt: str,
    temperature: float,
) -> Any:
    """Call Grok via xAI's OpenAI-compatible chat completions endpoint."""
    url = f"{_GROK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _GROK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot reach xAI API at {_GROK_BASE_URL}. Check your internet connection."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        status = resp.status_code
        if status == 401:
            raise ConfigurationError(
                "Invalid Grok API key. Check your key at https://console.x.ai/"
            ) from exc
        raise RuntimeError(f"Grok API returned HTTP {status}: {resp.text[:200]}") from exc

    text: str = resp.json()["choices"][0]["message"]["content"]
    return _parse_json(text)


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
    provider: Provider = Provider.GROK,
    GROK_api_key: str | None = None,  # kept for backward compat, unused
    grok_api_key: str | None = None,
    ollama_model: str = OLLAMA_DEFAULT_MODELS[0],
    ollama_base_url: str = _OLLAMA_BASE_URL,
    temperature: float = 0.7,
) -> Any:
    """Dispatch a prompt to the selected AI provider and return parsed JSON."""
    if provider is Provider.GROK:
        key = _resolve_grok_key(grok_api_key)
        return _call_grok(key, prompt, temperature)

    if provider is Provider.OLLAMA:
        return _call_ollama(ollama_model, prompt, temperature, ollama_base_url)

    raise ValueError(f"Unknown provider: {provider}")  # pragma: no cover
