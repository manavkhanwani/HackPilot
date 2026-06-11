"""Data models for HackPilot."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class HackathonContext:
    theme: str
    team_size: int
    duration_hours: int
    preferred_tech: list[str] = field(default_factory=list)


@dataclass
class ProjectIdea:
    title: str
    problem_statement: str
    solution_summary: str
    innovation_score: int  # 1–10
    difficulty: Literal["Easy", "Medium", "Hard"]


@dataclass
class FeasibilityReport:
    is_feasible: bool
    confidence: int  # 1–10
    risks: list[str]
    recommendations: list[str]


@dataclass
class Milestone:
    title: str
    description: str
    time_offset_hours: int


@dataclass
class ExecutionPlan:
    mvp_scope: list[str]
    stretch_goals: list[str]
    milestones: list[Milestone]


@dataclass
class ElevatorPitch:
    tagline: str
    pitch_text: str


@dataclass
class ReadmeDraft:
    markdown: str
