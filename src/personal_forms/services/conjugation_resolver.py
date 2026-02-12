from src.personal_forms.models import Verb, VerbForm
from src.common.choices import (
    Tense,
    Pronoun,
    AuxiliaryVerb,
    AuxiliaryConjugation,
)


class ConjugationResolver:

    @classmethod
    def conjugate(cls, verb: Verb, tense: Tense, pronoun: Pronoun) -> str:
        if tense in (Tense.PRAESENS, Tense.PRAETERITUM):
            return cls._simple_tense(verb, tense, pronoun)

        if tense == Tense.PERFEKT:
            return cls._perfekt(verb, pronoun)

        raise ValueError(f"Unsupported tense: {tense}")

    @staticmethod
    def _simple_tense(verb: Verb, tense: Tense, pronoun: Pronoun) -> str:
        try:
            form = VerbForm.objects.get(
                verb=verb,
                tense=tense.value,
                pronoun=pronoun.value,
            )
        except VerbForm.DoesNotExist:
            raise ValueError(
                f"Missing form for {verb.infinitive} "
                f"{tense.value} {pronoun.value}"
            )

        return form.form

    @staticmethod
    def _perfekt(verb: Verb, pronoun: Pronoun) -> str:
        if not verb.auxiliary:
            raise ValueError(
                f"Verb {verb.infinitive} has no auxiliary defined"
            )

        if not verb.participle_ii:
            raise ValueError(
                f"Verb {verb.infinitive} has no participle_ii defined"
            )

        auxiliary_enum = AuxiliaryVerb(verb.auxiliary)

        aux_form = AuxiliaryConjugation.get(
            auxiliary_enum,
            pronoun
        )

        return f"{pronoun.value} {aux_form} {verb.participle_ii}"