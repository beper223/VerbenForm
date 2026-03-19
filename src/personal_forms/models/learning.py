import uuid
import json

from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
    get_language,
)

from src.common.choices import CEFRLevel, SkillType
from src.personal_forms.models.VerbForms import Verb


class VerbGroup(models.Model):
    """Контейнер для глаголов, который можно использовать в разных типах тренировок"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verb_groups",
        verbose_name=_("Autor"),
        default='fdd5cf8e-3605-4a30-bbd5-c8f68738f9be'
    )
    # course = models.ForeignKey(
    #     'Course',
    #     on_delete=models.CASCADE,
    #     related_name="verb_groups",
    #     verbose_name=_("Kurse")
    # )
    title = models.CharField(_("Titel des Wortschatzes"), max_length=200)
    verbs = models.ManyToManyField(
        Verb,
        related_name="verb_groups",
        verbose_name=_("Verben")
    )

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class LearningUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name="learning_units",
        verbose_name=_("Kurs"),
    )
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

    verb_group = models.ForeignKey(
        VerbGroup,
        # on_delete=models.CASCADE,
        on_delete=models.SET_NULL,
        related_name="units",
        null=True,
        blank=True,
        verbose_name=_("Wortschatz")
    )

    class Meta:
        verbose_name = _("Lerneinheit")
        verbose_name_plural = _("Lerneinheiten")
        indexes = [
            models.Index(fields=["course", "order"]),
            models.Index(fields=["course", "level"]),
        ]

    @property
    def verbs(self):
        if self.verb_group:
            return self.verb_group.verbs
        return Verb.objects.none()

class Course(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", _("Öffentlich")
        PRIVATE = "private", _("Privat")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        verbose_name=_("Kurstitel"),
        max_length=200,
    )
    description = models.TextField(
        verbose_name=_("Beschreibung"),
        default='{}',
        blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("Autor"),
        limit_choices_to={'role__in': ['teacher', 'admin']},
    )
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        verbose_name=_("Sichtbarkeit"),
    )
    assigned_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="assigned_courses",
        verbose_name=_("Zugewiesene Schüler"),
        limit_choices_to={'role': 'student'},
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
        verbose_name = _("Kurs")
        verbose_name_plural = _("Kurse")
        indexes = [
            models.Index(fields=["author", "visibility"]),
            models.Index(fields=["visibility"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.author})"

    def is_accessible_by(self, user):
        """Check if user can access this course."""
        if self.author == user:
            return True
        if self.visibility == self.Visibility.PUBLIC:
            return user.role == 'student'
        if self.visibility == self.Visibility.PRIVATE:
            return self.assigned_students.filter(id=user.id).exists()
        return False

    @property
    def translated_description(self):
        """Возвращает описание на текущем языке пользователя или на английском/первом доступном"""
        try:
            data = json.loads(self.description)
        except (ValueError, TypeError):
            return self.description  # Если в базе не JSON, возвращаем как есть

        curr_lang = get_language()
        return data.get(curr_lang) or data.get(settings.LANGUAGE_CODE) or next(iter(data.values()), "")

    @property
    def description_preview(self):
        """Возвращает первые две непустые строки описания"""
        text = self.translated_description
        if not text:
            return ""

        # Разрезаем текст на строки, убираем лишние пробелы и пустые строки
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Берем только первые две строки и соединяем их обратно
        return "\n".join(lines[:2])

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
