from django.db import models
from src.common.choices import Tense, CEFRLevel
from src.personal_forms.models import Verb

class LearningUnit(models.Model):
    level = models.CharField(
        max_length=2,
        choices=CEFRLevel.choices(),
    )

    tense = models.CharField(
        max_length=15,
        choices=Tense.choices(),
    )

    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    verbs = models.ManyToManyField(
        Verb,
        blank=True,
        related_name="learning_units"
    )
