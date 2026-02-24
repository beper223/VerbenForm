import random
from dataclasses import dataclass
from typing import List

from src.personal_forms.models import Verb
from src.personal_forms.models import LearningAtom, TrainingCard
from src.personal_forms.services import ConjugationResolver, DistractorGenerator
from src.common.choices import SkillType, Tense, Pronoun



class CardFactory:

    def __init__(self):
        self.distractor_generator = DistractorGenerator()

    def build_card(self, atom: LearningAtom) -> TrainingCard:
        if atom.skill_type == SkillType.TRANSLATION:
            return self._translation_card(atom)

        if atom.skill_type in (
            SkillType.PRAESENS,
            SkillType.PRAETERITUM,
            SkillType.PERFEKT,
        ):
            return self._conjugation_card(atom)

        raise ValueError(f"Unsupported skill type: {atom.skill_type}")

    # ---------------------------------------------------

    def _translation_card(self, atom: LearningAtom) -> TrainingCard:
        verb = atom.verb

        correct = verb.translation  # предполагаем что есть поле

        distractors = self.distractor_generator.translation_distractors(
            verb=verb,
            limit=3,
        )

        options = distractors + [correct]
        random.shuffle(options)

        return TrainingCard(
            question=verb.infinitive,
            options=options,
            correct_answer=correct,
        )

    # ---------------------------------------------------

    def _conjugation_card(self, atom: LearningAtom) -> TrainingCard:
        verb = atom.verb
        pronoun_enum = Pronoun(atom.pronoun)
        tense = Tense(atom.skill_type)

        correct = ConjugationResolver.conjugate(
            verb=verb,
            tense=tense,
            pronoun=pronoun_enum,
        )

        # Если Perfekt — убираем местоимение
        if tense == Tense.PERFEKT:
            correct = self._strip_pronoun(correct, pronoun_enum)

        distractors = self.distractor_generator.conjugation_distractors(
            verb=verb,
            tense=tense,
            pronoun=pronoun_enum,
            correct_answer=correct,
            limit=3,
        )

        options = distractors + [correct]
        random.shuffle(options)

        question = f"{verb.infinitive}\n{pronoun_enum.value}"

        return TrainingCard(
            question=question,
            options=options,
            correct_answer=correct,
        )

    # ---------------------------------------------------

    @staticmethod
    def _strip_pronoun(full_phrase: str, pronoun: Pronoun) -> str:
        prefix = pronoun.value + " "
        if full_phrase.startswith(prefix):
            return full_phrase[len(prefix):]
        return full_phrase