from django.core.cache import cache

from src.personal_forms.models import LearningUnit
from src.personal_forms.services import (
    CachedTrainingEngine,
    ProgressService,
    CardFactory
)

from src.personal_forms.domain import (
    LearningAtom,
    NextCard,
    AnswerResult,
)


class TrainingService:

    CARD_TTL = 60

    def __init__(self):
        self.engine = CachedTrainingEngine()
        self.factory = CardFactory()
        self.progress = ProgressService()

    # ============================================================
    # GET NEXT CARD
    # ============================================================

    def get_next_card(self, *, user, learning_unit: LearningUnit, language: str) -> NextCard | None:
        # 1. Что учим?
        atom: LearningAtom | None = self.engine.get_next_atom(
            user=user,
            learning_unit=learning_unit,
        )
        if not atom: return None

        # 2. ОДНИМ запросом тянем все глаголы юнита со всеми формами и переводами
        # Грузим данные (prefetch_related внутри)
        all_verbs = list(
            learning_unit.verbs.prefetch_related('translations', 'forms').all()
        )

        # Находим текущий глагол в списке
        verb = next((v for v in all_verbs if v.id == atom.verb_id), None)
        if not verb: return None

        # 3. Создаем карточку через фабрику
        card = self.factory.build_card(
            verb=verb,
            atom=atom,
            unit_verbs=all_verbs,
            language=language
        )

        # 4. Кешируем для проверки
        card_id = f"card:{user.id}"
        self._cache_card(
            card_id,
            atom,
            learning_unit.id,
            card.correct_answer
        )

        return NextCard(
            card_id=card_id,
            question=card.question,
            options=card.options,
        )

    @staticmethod
    def _cache_card(card_id, atom, unit_id, correct_answer):
        """
        Сохраняем метаданные карточки в кеш.
        Мы сохраняем всё, что нужно для ProgressService, чтобы не лезть в БД лишний раз.
        """
        cache_data = {
            "verb_id": atom.verb_id,
            "skill_type": atom.skill_type,
            "pronoun": atom.pronoun,
            "unit_id": unit_id,  # Сохраняем ID юнита, чтобы потом сбросить его кеш
            "correct_answer": correct_answer,
        }

        # TTL (время жизни) обычно ставится 5-10 минут.
        # Если пользователь не ответил за это время, карточка "протухает".
        cache.set(card_id, cache_data, timeout=600)

    # ============================================================
    # ANSWER
    # ============================================================

    def submit_answer(self, *, user, card_id: str, user_answer: str) -> AnswerResult:
        # 1. Достаем данные из "памяти"
        card_data = cache.get(card_id)
        if not card_data:
            raise ValueError("Card expired")

        # 2. Сверяем ответ
        is_correct = user_answer.strip() == card_data["correct_answer"].strip()

        # 3. Находим прогресс в базе
        progress = self.progress.get_or_create_progress(
            user=user,
            verb_id=card_data["verb_id"],
            skill_type=card_data["skill_type"],
            pronoun=card_data["pronoun"]
        )

        # 4. ЗАПИСЫВАЕМ РЕЗУЛЬТАТ
        # Мы передаем unit_id, чтобы внутри record_answer сбросить кеш!
        self.progress.record_answer(
            progress=progress,
            is_correct=is_correct,
            unit_id=card_data["unit_id"]  # <-- Передаем для инвалидации кеша
        )

        cache.delete(card_id)

        return AnswerResult(
            correct=is_correct,
            correct_answer=card_data["correct_answer"],
            mastered=progress.mastered,
            streak=progress.streak,
        )
