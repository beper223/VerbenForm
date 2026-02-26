import random
from typing import List

from django.conf import settings

from src.personal_forms.models import Verb, VerbForm, LearningUnit, VerbTranslation
from src.personal_forms.services import ConjugationResolver
from src.common.choices import Tense, Pronoun, AuxiliaryVerb


class DistractorGenerator:

    # ==================================================
    # TRANSLATION (для языков != основной)
    # ==================================================

    @staticmethod
    def translation_distractors(
            *,
        verb: Verb,
        learning_unit: LearningUnit,
        language: str,
        limit: int = 3,
    ) -> List[str]:

        main_language = settings.LANGUAGE_CODE

        if language == main_language:
            raise ValueError("Translation distractors are not available for main language.")

        # 1. Получаем ID всех глаголов в этом уроке
        # (Это эффективно, так как Django часто уже держит их в кеше)
        unit_verb_ids = learning_unit.verbs.values_list('id', flat=True)

        # 2. Идем в таблицу переводов
        distractors_qs = VerbTranslation.objects.filter(
            language_code=language,  # Только нужный язык
            verb_id__in=unit_verb_ids  # Только из этого урока
        ).exclude(verb_id=verb.id)  # Кроме правильного ответа

        # 3. Берем только текст перевода
        distractors = list(distractors_qs.values_list("translation", flat=True))

        # 4. Перемешиваем и ограничиваем
        random.shuffle(distractors)
        return distractors[:limit]

    # ==================================================
    # CONJUGATION
    # ==================================================

    def conjugation_distractors(
        self,
        *,
        verb: Verb,
        tense: Tense,
        pronoun: Pronoun,
        correct_answer: str,
        limit: int = 3,
    ) -> List[str]:

        if tense in (Tense.PRAESENS, Tense.PRAETERITUM):
            return self._simple_tense_distractors(
                verb=verb,
                tense=tense,
                correct_answer=correct_answer,
                limit=limit,
            )

        if tense == Tense.PERFEKT:
            return self._perfekt_distractors(
                verb=verb,
                correct_answer=correct_answer,
                limit=limit,
            )

        return []

    # --------------------------------------------------

    def _simple_tense_distractors(
        self,
        *,
        verb: Verb,
        tense: Tense,
        correct_answer: str,
        limit: int,
    ) -> List[str]:

        forms = VerbForm.objects.filter(
            verb=verb,
            tense=tense.value,
        ).values_list("form", flat=True)

        forms_list = [f for f in forms if f != correct_answer]

        random.shuffle(forms_list)

        return forms_list[:limit]

    # --------------------------------------------------

    def _perfekt_distractors(
        self,
        *,
        verb: Verb,
        correct_answer: str,
        limit: int,
    ) -> List[str]:

        distractors = set()

        # 1️⃣ формы с другими местоимениями
        for pronoun in Pronoun:
            full = ConjugationResolver.conjugate(
                verb=verb,
                tense=Tense.PERFEKT,
                pronoun=pronoun,
            )

            stripped = self._strip_pronoun(full, pronoun)

            if stripped != correct_answer:
                distractors.add(stripped)

        participle = verb.participle_ii

        # 2️⃣ неправильный auxiliary
        wrong_aux = self._wrong_auxiliary(verb, participle)
        if wrong_aux:
            distractors.add(wrong_aux)

        # 3️⃣ неправильное окончание participle
        wrong_participle = self._wrong_participle(participle)
        if wrong_participle:
            aux = correct_answer.split(" ")[0]
            distractors.add(f"{aux} {wrong_participle}")

        # 4️⃣ убрать ge-
        if participle.startswith("ge"):
            aux = correct_answer.split(" ")[0]
            distractors.add(f"{aux} {participle[2:]}")

        # 5️⃣ добавить лишний ge-
        if not participle.startswith("ge"):
            aux = correct_answer.split(" ")[0]
            distractors.add(f"{aux} ge{participle}")

        distractors.discard(correct_answer)

        distractors_list = list(distractors)

        random.shuffle(distractors_list)

        return distractors_list[:limit]

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _strip_pronoun(full_phrase: str, pronoun: Pronoun) -> str:
        prefix = pronoun.value + " "
        if full_phrase.startswith(prefix):
            return full_phrase[len(prefix):]
        return full_phrase

    @staticmethod
    def _wrong_auxiliary(verb, participle: str) -> str | None:

        if not verb.auxiliary:
            return None

        if verb.auxiliary == AuxiliaryVerb.SEIN.value:
            wrong_aux = AuxiliaryVerb.HABEN
        else:
            wrong_aux = AuxiliaryVerb.SEIN

        from src.common.choices import AuxiliaryConjugation

        aux_form = AuxiliaryConjugation.get(
            wrong_aux,
            Pronoun.ICH,
        )

        return f"{aux_form} {participle}"

    @staticmethod
    def _wrong_participle(participle: str) -> str | None:

        if participle.endswith("en"):
            return participle[:-2] + "t"

        if participle.endswith("t"):
            return participle[:-1] + "en"

        return None

    @staticmethod
    def get_translation_field(language: str) -> str:

        # ожидаем что в settings есть что-то вроде:
        # SUPPORTED_LANGUAGES = {
        #     "en": "translation_en",
        #     "ru": "translation_ru",
        #     "uk": "translation_uk",
        # }

        try:
            return settings.SUPPORTED_LANGUAGES[language]
        except KeyError:
            raise ValueError(f"No translation field configured for language '{language}'")