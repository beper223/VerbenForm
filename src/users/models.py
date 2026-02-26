from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    # Язык обучения (для переводов)
    language = models.CharField(
        _("Sprache"),
        max_length=2,
        default="en"
    )

    # symmetrical=False важно, так как связь не взаимная (я твой учитель, но ты не мой)
    teachers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name="students",
        blank=True,
        verbose_name=_("Lehrer")
    )

    class Meta:
        verbose_name = _("Benutzer")
        verbose_name_plural = _("Benutzer")


class StudentInvitation(models.Model):
    email = models.EmailField(_("E-Mail"))
    code = models.CharField(_("Einladungscode"), max_length=12, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} (Teacher: {self.teacher.username})"
