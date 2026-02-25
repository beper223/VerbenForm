# src/personal_forms/domain.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LearningAtom:
    verb_id: int
    skill_type: str
    pronoun: str | None


@dataclass(frozen=True)
class TrainingCard:
    question: str
    options: list[str]
    correct_answer: str


@dataclass(frozen=True)
class NextCard:
    card_id: str
    question: str
    options: list[str]

@dataclass
class AnswerResult:
    correct: bool
    correct_answer: str
    mastered: bool
    streak: int