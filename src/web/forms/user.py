from django import forms
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
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
        fields = ("email", "language")

class InvitationForm(forms.ModelForm):
    # Явно определяем поле, чтобы задать начальное значение динамически
    expires_at = forms.DateTimeField(
        label=_("Gültig bis"),
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            },
            # Формат важен для корректного отображения в браузере (HTML5)
            format='%Y-%m-%dT%H:%M'
        )
    )
    class Meta:
        model = StudentInvitation
        fields = ['email', 'expires_at']
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
        # Если это создание новой формы (не редактирование), ставим дату +7 дней
        if not self.instance.pk:
            expiry_date = timezone.now() + timedelta(days=7)
            # Убираем секунды и микросекунды для соответствия формату datetime-local
            self.initial['expires_at'] = expiry_date.strftime('%Y-%m-%dT%H:%M')