import random

from django.core.cache import cache

from src.personal_forms.models import LearningUnit, Verb
from src.personal_forms.services import (
    CachedTrainingEngine,
    DistractorGenerator,
    ProgressService,
    ConjugationResolver,
)

from src.common.choices import SkillType, Tense, Pronoun
from src.personal_forms.domain import (
    LearningAtom,
    NextCard,
    AnswerResult
)


class TrainingService:

    CARD_TTL = 60

    def __init__(self):
        self.engine = CachedTrainingEngine()
        self.distractors = DistractorGenerator()
        self.progress_service = ProgressService()

    # ============================================================
    # GET NEXT CARD
    # ============================================================

    def get_next_card(self, *, user, learning_unit: LearningUnit, language: str) -> NextCard | None:

        atom: LearningAtom | None = self.engine.get_next_atom(
            user=user,
            learning_unit=learning_unit,
        )

        if not atom:
            return None

        verbs_map = {
            v.id: v
            for v in learning_unit.verbs.prefetch_related('translations').all()
        }
        verb = verbs_map.get(atom.verb_id)
        if verb is None:
            # На всякий случай: verb мог быть удалён/отвязан от юнита
            return None

        correct_answer = self._resolve_correct_answer(
            atom=atom,
            verb=verb,
            language=language,
        )

        distractors = self._resolve_distractors(
            atom=atom,
            verb=verb,
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
                "verb_id": atom.verb_id,
                "skill_type": atom.skill_type,
                "pronoun": atom.pronoun,
                "correct_answer": correct_answer,
            },
            timeout=self.CARD_TTL,
        )

        return NextCard(
            card_id=card_id,
            question=self._build_question(atom=atom, verb=verb),
            options=choices,
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

    @staticmethod
    def _build_question(*, atom: LearningAtom, verb: Verb) -> str:
        if atom.skill_type == SkillType.TRANSLATION:
            return verb.infinitive

        # Для conjugation: показываем глагол + местоимение
        pronoun = atom.pronoun or ""
        return f"{verb.infinitive}\n{pronoun}"

    @staticmethod
    def _resolve_correct_answer(*, atom: LearningAtom, verb: Verb, language: str) -> str:

        if atom.skill_type == SkillType.TRANSLATION:
            # Ищем перевод в связанной модели VerbTranslation
            translation_obj = verb.translations.filter(language_code=language).first()

            if not translation_obj:
                # Фолбек: если перевода нет, возвращаем инфинитив (или вызываем ошибку)
                return verb.infinitive

            return translation_obj.translation

        if atom.skill_type == SkillType.PRAESENS:
            tense = Tense.PRAESENS
        elif atom.skill_type == SkillType.PRAETERITUM:
            tense = Tense.PRAETERITUM
        elif atom.skill_type == SkillType.PERFEKT:
            tense = Tense.PERFEKT
        else:
            raise ValueError("Unsupported skill type")

        if not atom.pronoun:
            raise ValueError("Pronoun is required for conjugation tasks")
        pronoun_enum = Pronoun(atom.pronoun)

        full_phrase = ConjugationResolver.conjugate(
            verb=verb,
            tense=tense,
            pronoun=pronoun_enum,
        )

        prefix = f"{pronoun_enum.value} "
        if full_phrase.startswith(prefix):
            return full_phrase[len(prefix):]

        return full_phrase

    def _resolve_distractors(
            self,
            *,
            atom: LearningAtom,
            verb: Verb,
            learning_unit,
            language: str,
            correct_answer: str,
    ):

        if atom.skill_type == SkillType.TRANSLATION:
            return self.distractors.translation_distractors(
                verb=verb,
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

        if not atom.pronoun:
            return []
        pronoun_enum = Pronoun(atom.pronoun)

        return self.distractors.conjugation_distractors(
            verb=verb,
            tense=tense,
            pronoun=pronoun_enum,
            correct_answer=correct_answer,
        )