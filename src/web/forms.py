from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class RegistrationForm(UserCreationForm):
    invitation_code = forms.CharField(
        max_length=12,
        required=False,
        help_text="Если у вас есть код от учителя, введите его здесь."
    )
    # Добавляем выбор языка
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        label="Язык перевода (ваш родной язык)"
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "language")