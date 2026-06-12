"""Tests for the three new cross-cutting concerns:
  - Language selection logic (Feature 1)
  - AI Provider selection logic (Feature 2)
  - API key resolution logic (Feature 3 – BYOK)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hackpilot.ai_provider import (
    OLLAMA_DEFAULT_MODELS,
    ConfigurationError,
    Provider,
    _call_ollama,
    _resolve_GROK_key,
    call,
)
from hackpilot.language import (
    LANGUAGE_OPTIONS,
    Language,
    language_instruction,
)
from hackpilot.models import (
    ExecutionPlan,
    FeasibilityReport,
    HackathonContext,
    ProjectIdea,
)
from hackpilot.prompts import (
    elevator_pitch,
    feasibility_analyzer,
    idea_generator,
    readme_generator,
    execution_planner,
)


# ─────────────────────────────────────────────────────────────────────────────
# Feature 1 – Language selection
# ─────────────────────────────────────────────────────────────────────────────


class TestLanguageEnum:
    def test_all_languages_in_options(self) -> None:
        for lang in Language:
            assert lang.value in LANGUAGE_OPTIONS

    def test_english_is_default_index(self) -> None:
        assert LANGUAGE_OPTIONS[0] == Language.ENGLISH.value

    def test_language_instruction_non_empty(self) -> None:
        for lang in Language:
            instr = language_instruction(lang)
            assert len(instr) > 10, f"Empty instruction for {lang}"

    def test_hindi_instruction_contains_hindi_text(self) -> None:
        instr = language_instruction(Language.HINDI)
        # Must contain Devanagari characters
        assert any("\u0900" <= ch <= "\u097f" for ch in instr)

    def test_marathi_instruction_contains_marathi_text(self) -> None:
        instr = language_instruction(Language.MARATHI)
        assert any("\u0900" <= ch <= "\u097f" for ch in instr)

    def test_instructions_instruct_json_keys_in_english(self) -> None:
        """Non-English instructions must still mention JSON keys stay in English."""
        for lang in (Language.HINDI, Language.MARATHI):
            instr = language_instruction(lang)
            assert "JSON keys" in instr, f"Missing JSON key note for {lang}"


class TestPromptLanguageInjection:
    """Verify that language instructions are injected into every prompt builder."""

    @pytest.fixture
    def ctx(self) -> HackathonContext:
        return HackathonContext("AI", 2, 24, ["Python"])

    @pytest.fixture
    def idea(self) -> ProjectIdea:
        return ProjectIdea("X", "prob", "sol", 7, "Medium")

    @pytest.fixture
    def feasibility(self) -> FeasibilityReport:
        return FeasibilityReport(True, 8, ["r1"], ["rec1"])

    @pytest.fixture
    def plan(self) -> ExecutionPlan:
        from hackpilot.models import Milestone
        return ExecutionPlan(["f1"], ["s1"], [Milestone("m", "d", 2)])

    def test_idea_generator_hindi(self, ctx: HackathonContext) -> None:
        prompt = idea_generator(ctx, Language.HINDI)
        assert language_instruction(Language.HINDI) in prompt

    def test_idea_generator_marathi(self, ctx: HackathonContext) -> None:
        prompt = idea_generator(ctx, Language.MARATHI)
        assert language_instruction(Language.MARATHI) in prompt

    def test_feasibility_analyzer_hindi(
        self, idea: ProjectIdea, ctx: HackathonContext
    ) -> None:
        prompt = feasibility_analyzer(idea, ctx, Language.HINDI)
        assert language_instruction(Language.HINDI) in prompt

    def test_execution_planner_hindi(
        self,
        idea: ProjectIdea,
        feasibility: FeasibilityReport,
        ctx: HackathonContext,
    ) -> None:
        prompt = execution_planner(idea, feasibility, ctx, Language.HINDI)
        assert language_instruction(Language.HINDI) in prompt

    def test_elevator_pitch_marathi(
        self, idea: ProjectIdea, plan: ExecutionPlan
    ) -> None:
        prompt = elevator_pitch(idea, plan, Language.MARATHI)
        assert language_instruction(Language.MARATHI) in prompt

    def test_readme_generator_hindi(
        self, idea: ProjectIdea, plan: ExecutionPlan, ctx: HackathonContext
    ) -> None:
        prompt = readme_generator(idea, plan, ctx, Language.HINDI)
        assert language_instruction(Language.HINDI) in prompt

    def test_default_language_is_english(self, ctx: HackathonContext) -> None:
        prompt_default = idea_generator(ctx)
        prompt_explicit = idea_generator(ctx, Language.ENGLISH)
        assert prompt_default == prompt_explicit


# ─────────────────────────────────────────────────────────────────────────────
# Feature 2 – Provider selection
# ─────────────────────────────────────────────────────────────────────────────


class TestProviderEnum:
    def test_both_providers_exist(self) -> None:
        assert Provider.GROK in Provider
        assert Provider.OLLAMA in Provider

    def test_ollama_default_models_non_empty(self) -> None:
        assert len(OLLAMA_DEFAULT_MODELS) >= 1

    def test_known_models_present(self) -> None:
        assert "llama3" in OLLAMA_DEFAULT_MODELS
        assert "mistral" in OLLAMA_DEFAULT_MODELS


class TestCallDispatchesToGROK:
    def test_GROK_path_called(self) -> None:
        with (
            patch("hackpilot.ai_provider._resolve_GROK_key", return_value="key"),
            patch(
                "hackpilot.ai_provider._call_GROK",
                return_value={"ok": True},
            ) as mock_GROK,
        ):
            result = call("prompt", provider=Provider.GROK, GROK_api_key="key")

        mock_GROK.assert_called_once()
        assert result == {"ok": True}

    def test_ollama_path_called(self) -> None:
        with patch(
            "hackpilot.ai_provider._call_ollama",
            return_value={"ok": True},
        ) as mock_ollama:
            result = call(
                "prompt",
                provider=Provider.OLLAMA,
                ollama_model="mistral",
            )

        mock_ollama.assert_called_once()
        assert result == {"ok": True}

    def test_ollama_connection_error_raises_runtime(self) -> None:
        import requests as req

        with patch(
            "hackpilot.ai_provider.requests.post",
            side_effect=req.exceptions.ConnectionError("refused"),
        ):
            with pytest.raises(RuntimeError, match="Cannot reach Ollama"):
                _call_ollama("mistral", "prompt", 0.7)

    def test_ollama_http_error_raises_runtime(self) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = __import__(
            "requests"
        ).exceptions.HTTPError("404")
        mock_resp.status_code = 404
        mock_resp.text = "model not found"

        with patch("hackpilot.ai_provider.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="HTTP 404"):
                _call_ollama("unknown-model", "prompt", 0.7)

    def test_ollama_non_json_raises_runtime(self) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"response": "not json at all!!!"}

        with patch("hackpilot.ai_provider.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="non-JSON"):
                _call_ollama("mistral", "prompt", 0.7)


# ─────────────────────────────────────────────────────────────────────────────
# Feature 3 – API key resolution (BYOK)
# ─────────────────────────────────────────────────────────────────────────────


class TestResolveGROKKey:
    def test_user_supplied_key_takes_priority(self) -> None:
        key = _resolve_GROK_key("user-supplied-key")
        assert key == "user-supplied-key"

    def test_whitespace_only_key_is_ignored(self) -> None:
        """A key consisting only of whitespace must fall through to secrets."""
        mock_st = MagicMock()
        mock_st.secrets.get.return_value = "secret-key"

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            key = _resolve_GROK_key("   ")

        assert key == "secret-key"

    def test_empty_string_falls_through_to_secrets(self) -> None:
        mock_st = MagicMock()
        mock_st.secrets.get.return_value = "from-secrets"

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            key = _resolve_GROK_key("")

        assert key == "from-secrets"

    def test_none_falls_through_to_secrets(self) -> None:
        mock_st = MagicMock()
        mock_st.secrets.get.return_value = "from-secrets"

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            key = _resolve_GROK_key(None)

        assert key == "from-secrets"

    def test_no_key_anywhere_raises_configuration_error(self) -> None:
        mock_st = MagicMock()
        mock_st.secrets.get.return_value = ""

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            with pytest.raises(ConfigurationError, match="No GROK API key"):
                _resolve_GROK_key("")

    def test_streamlit_import_error_raises_configuration_error(self) -> None:
        """When Streamlit is unavailable (e.g. CLI context), raise ConfigurationError."""
        with patch.dict("sys.modules", {"streamlit": None}):
            with pytest.raises(ConfigurationError):
                _resolve_GROK_key(None)

    def test_key_stripped_of_whitespace(self) -> None:
        key = _resolve_GROK_key("  my-key  ")
        assert key == "my-key"

    def test_user_key_never_falls_through_to_secrets(self) -> None:
        """Even if secrets has a different key, user-supplied wins."""
        mock_st = MagicMock()
        mock_st.secrets.get.return_value = "secrets-key"

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            key = _resolve_GROK_key("byok-key")

        assert key == "byok-key"
        mock_st.secrets.get.assert_not_called()
