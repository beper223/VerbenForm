import random

from src.personal_forms.services.resolvers.registry import SKILL_RESOLVERS
from src.personal_forms.domain import TrainingCard


class CardFactory:
    """Отвечает только за сборку контента карточки"""

    @staticmethod
    def build_card(verb, atom, unit_verbs, language: str) -> TrainingCard:
        resolver = SKILL_RESOLVERS.get(atom.skill_type)
        if not resolver:
            raise ValueError(f"No resolver for: {atom.skill_type}")

        # 2. Генерируем правильный ответ и дистракторы
        correct_answer = resolver.get_correct_answer(verb, atom, language)
        distractors = resolver.get_distractors(verb, atom, unit_verbs, language)

        # 3. Собираем варианты ответа
        options = distractors + [correct_answer]
        random.shuffle(options)

        # 4. Формируем текст вопроса
        question = CardFactory._get_question(verb, atom)

        return TrainingCard(
            question=question,
            options=options,
            correct_answer=correct_answer
        )

    # ---------------------------------------------------

    @staticmethod
    def _get_question(verb, atom) -> str:
        if atom.skill_type == "translation":
            return verb.infinitive
        return f"{verb.infinitive}\n({atom.pronoun})"