# src/personal_forms/services/training_service.py

import random
from dataclasses import dataclass
from typing import List
from django.core.cache import cache

from src.personal_forms.models import LearningUnit, Verb
from src.personal_forms.services import (
    CachedTrainingEngine,
    DistractorGenerator,
    ProgressService,
    ConjugationResolver,
)

from src.common.choices import SkillType, Tense, Pronoun

@dataclass(frozen=True)
class LearningAtom:
    verb: Verb
    skill_type: SkillType
    pronoun: Pronoun

@dataclass
class TrainingCard:
    question: str
    options: List[str]
    correct_answer: str

@dataclass
class TrainingCard:
    card_id: str
    verb: str
    skill_type: str
    pronoun: str | None
    choices: list[str]


@dataclass
class AnswerResult:
    correct: bool
    correct_answer: str
    mastered: bool
    streak: int


class TrainingService:

    CARD_TTL = 60

    def __init__(self):
        self.engine = CachedTrainingEngine()
        self.distractors = DistractorGenerator()
        self.progress_service = ProgressService()

    # ============================================================
    # GET NEXT CARD
    # ============================================================

    def get_next_card(self, *, user, learning_unit: LearningUnit, language: str) -> TrainingCard | None:

        atom = self.engine.get_next_atom(
            user=user,
            learning_unit=learning_unit,
        )

        if not atom:
            return None

        correct_answer = self._resolve_correct_answer(
            atom=atom,
            learning_unit=learning_unit,
            language=language,
        )

        distractors = self._resolve_distractors(
            atom=atom,
            learning_unit=learning_unit,
            language=language,
            correct_answer=correct_answer,
        )

        choices = distractors[:3] + [correct_answer]
        random.shuffle(choices)

        card_id = f"card:{user.id}"

        cache.set(
            card_id,
            {
                "verb_id": atom.verb.id,
                "skill_type": atom.skill_type,
                "pronoun": atom.pronoun,
                "correct_answer": correct_answer,
            },
            timeout=self.CARD_TTL,
        )

        return TrainingCard(
            card_id=card_id,
            verb=atom.verb.infinitive,
            skill_type=atom.skill_type,
            pronoun=atom.pronoun,
            choices=choices,
        )

    # ============================================================
    # ANSWER
    # ============================================================

    def submit_answer(self, *, user, card_id: str, answer: str) -> AnswerResult:

        card_data = cache.get(card_id)
        if not card_data:
            raise ValueError("Card expired")

        verb = Verb.objects.get(id=card_data["verb_id"])

        progress = self.progress_service.get_or_create_progress(
            user=user,
            verb=verb,
            skill_type=card_data["skill_type"],
            pronoun=card_data["pronoun"],
        )

        correct_answer = card_data["correct_answer"]
        is_correct = answer.strip() == correct_answer.strip()

        self.progress_service.record_answer(
            progress=progress,
            is_correct=is_correct,
        )

        cache.delete(card_id)

        return AnswerResult(
            correct=is_correct,
            correct_answer=correct_answer,
            mastered=progress.mastered,
            streak=progress.streak,
        )

    # ============================================================
    # INTERNALS
    # ============================================================

    def _resolve_correct_answer(self, *, atom, learning_unit, language: str) -> str:

        if atom.skill_type == SkillType.TRANSLATION:

            field_name = self.distractors.get_translation_field(language)
            return getattr(atom.verb, field_name)

        if atom.skill_type == SkillType.PRAESENS:
            tense = Tense.PRAESENS
        elif atom.skill_type == SkillType.PRAETERITUM:
            tense = Tense.PRAETERITUM
        elif atom.skill_type == SkillType.PERFEKT:
            tense = Tense.PERFEKT
        else:
            raise ValueError("Unsupported skill type")

        full_phrase = ConjugationResolver.conjugate(
            verb=atom.verb,
            tense=tense,
            pronoun=atom.pronoun,
        )

        prefix = f"{atom.pronoun} "
        if full_phrase.startswith(prefix):
            return full_phrase[len(prefix):]

        return full_phrase

    def _resolve_distractors(self, *, atom, learning_unit, language: str, correct_answer: str):

        if atom.skill_type == SkillType.TRANSLATION:
            return self.distractors.translation_distractors(
                verb=atom.verb,
                learning_unit=learning_unit,
                language=language,
            )

        if atom.skill_type == SkillType.PRAESENS:
            tense = Tense.PRAESENS
        elif atom.skill_type == SkillType.PRAETERITUM:
            tense = Tense.PRAETERITUM
        elif atom.skill_type == SkillType.PERFEKT:
            tense = Tense.PERFEKT
        else:
            return []

        return self.distractors.conjugation_distractors(
            verb=atom.verb,
            tense=tense,
            pronoun=atom.pronoun,
            correct_answer=correct_answer,
        )