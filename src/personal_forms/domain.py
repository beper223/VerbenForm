from __future__ import annotations
from dataclasses import dataclass

from src.common.choices import Pronoun


@dataclass(frozen=True)
class LearningAtom:
    verb_id: int
    skill_type: str
    pronoun: Pronoun | None


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