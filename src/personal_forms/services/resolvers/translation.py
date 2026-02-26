import random

from src.personal_forms.services.resolvers import BaseSkillResolver


class TranslationResolver(BaseSkillResolver):
    def get_correct_answer(self, verb, atom, language=None):
        # Ищем перевод в префетчнутом списке verb.translations.all()
        # language — это код языка (например, "ru")
        trans_obj = next(
            (t for t in verb.translations.all() if t.language_code == language),
            None
        )
        # Если перевода нет, возвращаем инфинитив (или можно бросать ошибку)
        return trans_obj.translation if trans_obj else verb.infinitive

    def get_distractors(self, verb, atom, unit_verbs, language=None, limit=3):
        distractors = []
        for v in unit_verbs:
            if v.id == verb.id:
                continue

                # Достаем перевод для "соседнего" глагола из памяти
            trans_obj = next(
                (t for t in v.translations.all() if t.language_code == language),
                None
            )
            if trans_obj:
                distractors.append(trans_obj.translation)

        random.shuffle(distractors)
        return distractors[:limit]