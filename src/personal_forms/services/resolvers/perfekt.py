import random
from typing import List, Set

from src.common.choices import Pronoun, AuxiliaryVerb, AuxiliaryConjugation
from src.personal_forms.services.resolvers import BaseSkillResolver


class PerfektResolver(BaseSkillResolver):

    def get_correct_answer(self, verb, atom, language: str = None) -> str:
        if not verb.auxiliary or not verb.participle_ii:
            return "[Perfekt data missing]"

        # Получаем форму вспомогательного глагола (например, "bin", "ist", "habe")
        pronoun_enum = Pronoun(atom.pronoun)
        aux_verb_enum = AuxiliaryVerb(verb.auxiliary)
        aux_form = AuxiliaryConjugation.get(aux_verb_enum, pronoun_enum)

        return f"{aux_form} {verb.participle_ii}"

    def get_distractors(self, verb, atom, unit_verbs, language: str = None, limit: int = 3) -> List[str]:
        correct_answer = self.get_correct_answer(verb, atom)
        distractors: Set[str] = set()

        participle = verb.participle_ii
        pronoun_enum = Pronoun(atom.pronoun)
        aux_verb_enum = AuxiliaryVerb(verb.auxiliary)

        # 1. Формы с другими вспомогательными глаголами (для других лиц)
        # Просто берем формы для всех лиц и убираем местоимение
        for p in Pronoun:
            aux_f = AuxiliaryConjugation.get(aux_verb_enum, p)
            distractors.add(f"{aux_f} {participle}")

        # 2. Ошибка: неверный вспомогательный глагол (sein вместо haben и наоборот)
        wrong_aux_enum = AuxiliaryVerb.HABEN if aux_verb_enum == AuxiliaryVerb.SEIN else AuxiliaryVerb.SEIN
        wrong_aux_form = AuxiliaryConjugation.get(wrong_aux_enum, pronoun_enum)
        distractors.add(f"{wrong_aux_form} {participle}")

        # 3. Ошибка: неправильное окончание причастия (t <-> en)
        wrong_participle = self._mutate_participle_ending(participle)
        if wrong_participle:
            current_aux = AuxiliaryConjugation.get(aux_verb_enum, pronoun_enum)
            distractors.add(f"{current_aux} {wrong_participle}")

        # 4. Ошибка: манипуляция с приставкой ge-
        current_aux = AuxiliaryConjugation.get(aux_verb_enum, pronoun_enum)
        if participle.startswith("ge"):
            distractors.add(f"{current_aux} {participle[2:]}")  # убираем ge-
        else:
            distractors.add(f"{current_aux} ge{participle}")  # добавляем ge-

        # Убираем правильный ответ, если он туда попал, и пустые строки
        distractors.discard(correct_answer)
        distractors_list = [d for d in distractors if d]

        random.shuffle(distractors_list)
        return distractors_list[:limit]

    @staticmethod
    def _mutate_participle_ending(participle: str) -> str:
        if participle.endswith("en"):
            return participle[:-2] + "t"
        if participle.endswith("t"):
            return participle[:-1] + "en"
        return ""