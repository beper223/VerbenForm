from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", _("Schüler")
        TEACHER = "teacher", _("Lehrer")
        ADMIN = "admin", _("Administrator")

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
        return self.role == self.Role.ADMIN

    def is_teacher(self):
        return self.role == self.Role.TEACHER

class StudentInvitation(models.Model):
    email = models.EmailField(_("E-Mail"))
    code = models.CharField(_("Einladungscode"), max_length=12, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite for {self.email} by {self.teacher.username}"
