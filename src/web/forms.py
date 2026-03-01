from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from src.users.models import StudentInvitation

User = get_user_model()

class RegistrationForm(UserCreationForm):
    invitation_code = forms.CharField(
        max_length=12,
        required=False,
        help_text="Если у вас есть код от учителя, введите его здесь."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "language")