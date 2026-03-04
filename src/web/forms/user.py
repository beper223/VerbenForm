from django import forms
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
    class Meta:
        model = StudentInvitation
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@example.com',
                'required': True
            })
        }
        labels = {
            'email': _("E-Mail-Adresse des Studenten")
        }