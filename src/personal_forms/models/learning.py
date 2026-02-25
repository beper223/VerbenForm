from dataclasses import dataclass
from typing import Optional, List

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from src.common.choices import Tense, CEFRLevel, SkillType
from src.personal_forms.models import Verb

@dataclass(frozen=True)
class LearningAtom:
    verb: Verb
    skill_type: str
    pronoun: Optional[str]

@dataclass
class TrainingCard:
    question: str
    options: List[str]
    correct_answer: str

class LearningUnit(models.Model):
    level = models.CharField(
        verbose_name=_("Niveau"),
        max_length=2,
        choices=CEFRLevel.choices(),
    )

    skill_type = models.CharField(
        verbose_name=_("Fähigkeit"),
        max_length=20,
        choices=SkillType.choices,
        default=SkillType.TRANSLATION
    )

    title = models.CharField(
        verbose_name=_("Überschrift"),
        max_length=200,
    )
    order = models.PositiveIntegerField()

    verbs = models.ManyToManyField(
        Verb,
        blank=True,
        related_name="learning_units"
    )

    class Meta:
        verbose_name = _("Lerneinheit")
        verbose_name_plural = _("Lerneinheiten")

class UserVerbProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verb_progress",
        verbose_name=_("Benutzer"),
    )

    verb = models.ForeignKey(
        Verb,
        on_delete=models.CASCADE,
        related_name="user_progress",
        verbose_name=_("Verb"),
    )

    skill_type = models.CharField(
        max_length=20,
        choices=SkillType.choices,
        verbose_name=_("Fähigkeit")
    )

    # Для translation = NULL
    pronoun = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Pronomen"),
        help_text=_("Leer bei Übersetzungsaufgaben"),
    )

    correct_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Richtige Antworten"),
    )

    wrong_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Falsche Antworten"),
    )

    # Anzahl der aufeinanderfolgenden richtigen Antworten
    streak = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Aktuelle Serie"),
        help_text=_("Anzahl der richtigen Antworten in Folge"),
    )

    mastered = models.BooleanField(
        default=False,
        verbose_name=_("Beherrscht"),
        help_text=_("Wird als gelernt betrachtet"),
    )

    last_answer_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Letzte Antwort"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Erstellt am"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Aktualisiert am"),
    )

    class Meta:
        verbose_name = _("Verbfortschritt")
        verbose_name_plural = _("Verbfortschritte")
        unique_together = (
            "user",
            "verb",
            "skill_type",
            "pronoun",
        )
        indexes = [
            models.Index(fields=["user", "skill_type"]),
            models.Index(fields=["user", "mastered"]),
            models.Index(fields=["user", "verb", "skill_type", "pronoun"]),
        ]

    def __str__(self):
        return (
            f"{self.user} | {self.verb.infinitive} | "
            f"{self.skill_type} | {self.pronoun or '-'}"
        )
