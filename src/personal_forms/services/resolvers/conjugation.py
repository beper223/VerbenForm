import random
from typing import List

from src.personal_forms.services.resolvers import BaseSkillResolver
from src.personal_forms.models import Verb
from src.personal_forms.domain import LearningAtom


class SimpleConjugationResolver(BaseSkillResolver):
    """
    Резолвер для Präsens и Präteritum.
    Использует данные из связанной модели VerbForm.
    """
    def get_correct_answer(self, verb: Verb, atom: LearningAtom, language: str = None) -> str:
        target_tense = self.SKILL_TO_TENSE.get(atom.skill_type)
        # Ищем форму в префетчнутых формах глагола
        form_obj = next((f for f in verb.forms.all()
                     if f.tense == target_tense and f.pronoun == atom.pronoun), None)
        if not form_obj:
            return f"[{atom.skill_type} form missing]"

        return form_obj.form

    def get_distractors(self, verb: Verb, atom, unit_verbs: List[Verb], language: str = None, limit: int = 3) -> List[str]:
        correct_answer = self.get_correct_answer(verb, atom)
        target_tense = self.SKILL_TO_TENSE.get(atom.skill_type)

        # Дистракторы — это другие формы этого же глагола в этом же времени
        # Используем set для автоматического удаления дубликатов
        # (например, "gehen" для wir и sie останется в одном экземпляре)
        all_forms = {
            f.form for f in verb.forms.all()
            if f.tense == target_tense
        }

        # Удаляем правильный ответ из множества
        all_forms.discard(correct_answer)

        distractors_list = list(all_forms)
        random.shuffle(distractors_list)
        return distractors_list[:limit]