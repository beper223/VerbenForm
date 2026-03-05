import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

def default_expiry():
    return timezone.now() + timedelta(days=7)

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", _("Schüler")
        TEACHER = "teacher", _("Lehrer")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Язык обучения (для переводов)
    language = models.CharField(
        _("Sprache"),
        max_length=10,
        choices=settings.LANGUAGES,  # Автоматически возьмет список из settings.py
        default=settings.LANGUAGE_CODE  # 'de'
    )

    # symmetrical=False важно, так как связь не взаимная (я твой учитель, но ты не мой)
    teachers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name="students",
        blank=True,
        verbose_name=_("Lehrer")
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_("Rolle"),
        help_text=_("Bestimmt die Benutzerrolle im System.")
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Geburtsdatum"),
        help_text=_("Geburtsdatum des Benutzers.")
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name=_("Profilbild"),
        help_text=_("Profilbild des Benutzers.")
    )

    class Meta:
        verbose_name = _("Benutzer")
        verbose_name_plural = _("Benutzer")

    def is_admin(self):
        return self.is_staff

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_teacher_admin(self):
        return self.role == self.Role.TEACHER or self.is_staff

class StudentInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("E-Mail"))
    code = models.CharField(_("Einladungscode"), max_length=12, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        _("Ablaufdatum"),
        default=default_expiry,
        help_text=_("Nach diesem Datum verliert der Code seine Gültigkeit")
    )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_active(self):
        return not self.is_used and not self.is_expired()

    def __str__(self):
        return f"Invite for {self.email} by {self.teacher.username}"
