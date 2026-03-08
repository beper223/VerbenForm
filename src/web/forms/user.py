import math

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.users.models import StudentInvitation

User = get_user_model()

class RegistrationForm(UserCreationForm):
    # Добавляем выбор языка
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        label="Язык перевода (ваш родной язык)"
    )
    role = forms.ChoiceField(choices=User.Role.choices)
    invitation_code = forms.CharField(
        max_length=12,
        required=False,
        help_text="Если у вас есть код от учителя, введите его здесь."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "email", "language", "role")

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "language")
        labels = {
            'first_name': _("Vorname"),
            'last_name': _("Nachname"),
            'email': _("E-Mail-Adresse"),
            'language': _("Lernsprache"),
        }

class InvitationForm(forms.ModelForm):
    days_valid = forms.IntegerField(
        label=_("Gültig für (Tage)"),
        initial=7,
        required=False,  # Чтобы можно было оставить пустым для значения по умолчанию
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '7'
        })
    )
    class Meta:
        model = StudentInvitation
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@example.com',
                'required': True
            }),
            # 'expires_at': forms.DateInput(attrs={
            #     'class': 'form-control',
            #     'type': 'datetime-local'
            # }),
        }
        labels = {
            'email': _("E-Mail-Adresse des Studenten")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если мы РЕДАКТИРУЕМ существующий объект
        if self.instance and self.instance.pk:
            if self.instance.expires_at:
                # Вычисляем разницу во времени
                now = timezone.now()
                delta = self.instance.expires_at - now

                # Переводим секунды в полные дни, округляя в большую сторону
                # Если осталось 1.5 дня, покажем 2. Если просрочено — покажем 0.
                days_left = math.ceil(delta.total_seconds() / 86400)

                self.initial['days_valid'] = max(0, days_left)

        # Если это СОЗДАНИЕ нового (pk еще нет)
        else:
            self.initial['days_valid'] = 7
