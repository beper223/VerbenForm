from django.db import models
from django.utils.translation import gettext_lazy as _
from src.common.choices import (
    VerbType,
    Pronoun,
    Tense,
    AuxiliaryVerb,
    CEFRLevel,
    GermanCase,
    PrepositionCaseRequirement,
    Reflexiv,
    LanguageCode
)


class Verb(models.Model):

    infinitive = models.CharField(
        _("Infinitivform"),
        max_length=50,
        unique=True
    )
    verb_type = models.CharField(
        _("Konjugation"),
        max_length=10,
        choices=VerbType.choices(),
        default=VerbType.REGULAR
    )
    level = models.CharField(
        _("Niveau"),
        max_length=2,
        choices=CEFRLevel.choices(),
        default=CEFRLevel.A1
    )
    reflexivitaet = models.CharField(
        _("Reflexivität"),
        max_length=16,
        choices=Reflexiv.choices(),
        default=Reflexiv.NREFL
    )
    is_trennbare = models.BooleanField(_("Trennbarkeit"),default=False)
    case = models.CharField(
        _("Kasusrektion"),
        max_length=3,
        choices=[
            (GermanCase.AKK.name, GermanCase.AKK.value),
            (GermanCase.DAT.name, GermanCase.DAT.value),
        ],
        blank=True,
        null=True,
    )

    # nur für Perfekt
    auxiliary = models.CharField(
        _("Hilfsverb"),
        max_length=10,
        choices=AuxiliaryVerb.choices(),
        blank=True,
        null=True)  # 'haben' oder 'sein'
    participle_ii = models.CharField(_("Partizip 2"),max_length=50, blank=True, null=True)  # Beispel 'gegangen'

    class Meta:
        verbose_name = _("Verb")
        verbose_name_plural = _("Verben")

    def __str__(self):
        return self.infinitive

class VerbForm(models.Model):
    verb = models.ForeignKey(
        Verb,
        on_delete=models.CASCADE,
        related_name="forms"
    )
    tense = models.CharField(
        _("Zeitform"),
        max_length=15,
        choices=Tense.choices(),
    )
    pronoun = models.CharField(
        _("Pronomen"),
        max_length=20,
        choices=Pronoun.choices(),
    )
    form = models.CharField(
        _("Personalform"),
        max_length=50,
    )  # фактическая спряжённая форма

    class Meta:
        verbose_name = _("Personalform")
        verbose_name_plural = _("Personalformen")
        unique_together = ("verb", "tense", "pronoun")

    def __str__(self):
        return f"{self.verb.infinitive} - {self.tense} - {self.pronoun}: {self.form}"


class VerbTranslation(models.Model):
    verb = models.ForeignKey(
        Verb,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language_code = models.CharField(
        _("Sprache"),
        max_length=2,
        choices=LanguageCode.choices(),
    )
    translation = models.CharField(
        _("Übersetzung"),
        max_length=100,
    )

    class Meta:
        verbose_name = _("Übersetzung")
        verbose_name_plural = _("Übersetzungen")
        unique_together = ("verb", "language_code")

    def __str__(self):
        return f"{self.verb.infinitive} - {self.translation}"


class Preposition(models.Model):
    text = models.CharField(max_length=20, unique=True)
    case_requirement = models.CharField(
        max_length=5,
        choices=PrepositionCaseRequirement.choices(),
    )

    class Meta:
        verbose_name = _("Präposition")
        verbose_name_plural = _("Präpositionen")

    def __str__(self):
        return self.text


class VerbPreposition(models.Model):
    verb = models.ForeignKey(
        Verb,
        on_delete=models.CASCADE,
        related_name="prepositions",
    )
    preposition = models.ForeignKey(
        Preposition,
        on_delete=models.CASCADE,
        related_name="verbs",
    )
    case = models.CharField(
        max_length=3,
        choices=GermanCase.choices(),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Verb mit Präposition")
        verbose_name_plural = _("Verben mit Präposition")
        unique_together = ("verb", "preposition", "case")

    def __str__(self):
        if self.case:
            return f"{self.verb.infinitive} + {self.preposition.text} ({self.case})"
        return f"{self.verb.infinitive} + {self.preposition.text}"
