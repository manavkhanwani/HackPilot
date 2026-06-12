"""Language support for HackPilot.

Supported languages and their BCP-47 tags:
  - English (en)
  - Hindi  (hi)  हिन्दी
  - Marathi (mr) मराठी

GROK's multilingual capabilities are used directly — no external
translation APIs are required.  Each prompt is prefixed with an explicit
language instruction so the model responds exclusively in the chosen
language.
"""

from __future__ import annotations

from enum import Enum


class Language(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi (हिन्दी)"
    MARATHI = "Marathi (मराठी)"


# Human-readable display names for the Streamlit selectbox
LANGUAGE_OPTIONS: list[str] = [lang.value for lang in Language]

# BCP-47 tag for each language (used in prompt instructions)
_LANG_TAG: dict[Language, str] = {
    Language.ENGLISH: "English",
    Language.HINDI: "Hindi (हिन्दी)",
    Language.MARATHI: "Marathi (मराठी)",
}

# Instruction block injected at the top of every prompt
_LANG_INSTRUCTION: dict[Language, str] = {
    Language.ENGLISH: (
        "LANGUAGE REQUIREMENT: Respond ONLY in English. "
        "Do not mix in Hindi, Marathi, or any other language."
    ),
    Language.HINDI: (
        "भाषा आवश्यकता: केवल हिन्दी में उत्तर दें। "
        "अंग्रेज़ी, मराठी या किसी अन्य भाषा का उपयोग न करें। "
        "JSON keys must remain in English (as specified), "
        "but all string values must be in Hindi."
    ),
    Language.MARATHI: (
        "भाषा आवश्यकता: फक्त मराठीत उत्तर द्या। "
        "इंग्रजी, हिन्दी किंवा इतर कोणत्याही भाषेत उत्तर देऊ नका। "
        "JSON keys must remain in English (as specified), "
        "but all string values must be in Marathi."
    ),
}


def language_instruction(lang: Language) -> str:
    """Return the language enforcement instruction block for *lang*."""
    return _LANG_INSTRUCTION[lang]


def language_display_name(lang: Language) -> str:
    """Return the human-readable name for *lang*."""
    return _LANG_TAG[lang]
