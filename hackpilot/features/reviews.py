"""Review system for HackPilot.

Reviews are stored in a local JSON file (reviews.json) so they persist
across Streamlit sessions. The module exposes simple helpers for loading,
saving, and rendering reviews.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

_REVIEWS_FILE = Path("reviews.json")

CATEGORIES = ["Ideas", "Feasibility Analyzer", "Execution Planner", "Pitch Generator", "README Generator", "Overall App"]
STAR_LABELS = {1: "⭐ Poor", 2: "⭐⭐ Fair", 3: "⭐⭐⭐ Good", 4: "⭐⭐⭐⭐ Great", 5: "⭐⭐⭐⭐⭐ Excellent"}


@dataclass
class Review:
    reviewer_name: str
    category: str
    rating: int  # 1–5
    title: str
    body: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


def load_reviews() -> list[Review]:
    """Load reviews from the JSON file. Returns an empty list if the file doesn't exist."""
    if not _REVIEWS_FILE.exists():
        return []
    try:
        raw = json.loads(_REVIEWS_FILE.read_text(encoding="utf-8"))
        return [Review(**item) for item in raw]
    except Exception:
        return []


def save_review(review: Review) -> None:
    """Append a review to the JSON file."""
    reviews = load_reviews()
    reviews.append(review)
    _REVIEWS_FILE.write_text(
        json.dumps([asdict(r) for r in reviews], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def average_rating(reviews: list[Review]) -> float:
    if not reviews:
        return 0.0
    return sum(r.rating for r in reviews) / len(reviews)


def stars(rating: float) -> str:
    """Return a filled/empty star string for a given rating (supports half-stars via rounding)."""
    full = int(round(rating))
    return "⭐" * full + "☆" * (5 - full)
