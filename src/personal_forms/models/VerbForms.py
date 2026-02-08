from django.db import models
from src.common.choices import VerbType, Pronoun, Tense, AuxiliaryVerb, CEFRLevel


class Verb(models.Model):

    infinitive = models.CharField(max_length=50, unique=True)
    verb_type = models.CharField(
        max_length=10,
        choices=VerbType.choices(),
        default=VerbType.REGULAR)
    level = models.CharField(
        max_length=2,
        choices=CEFRLevel.choices(),
        default=CEFRLevel.A1
    )

    # nur für Perfekt
    auxiliary = models.CharField(
        max_length=10,
        choices=AuxiliaryVerb.choices(),
        blank=True,
        null=True)  # 'haben' oder 'sein'
    participle_ii = models.CharField(max_length=50, blank=True, null=True)  # Beispel 'gegangen'

    def __str__(self):
        return self.infinitive

class VerbForm(models.Model):
    verb = models.ForeignKey(
        Verb,
        on_delete=models.CASCADE,
        related_name="forms"
    )
    tense = models.CharField(
        max_length=15,
        choices=Tense.choices(),
    )
    pronoun = models.CharField(
        max_length=20,
        choices=Pronoun.choices(),
    )
    form = models.CharField(max_length=50)  # фактическая спряжённая форма

    class Meta:
        unique_together = ("verb", "tense", "pronoun")

    def __str__(self):
        return f"{self.verb.infinitive} - {self.tense} - {self.pronoun}: {self.form}"
