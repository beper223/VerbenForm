import math

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from src.users.models import StudentInvitation

User = get_user_model()

class RegistrationForm(UserCreationForm):
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        label="Übersetzungssprache (Ihre Muttersprache)"
    )
    role = forms.ChoiceField(choices=User.Role.choices)
    invitation_code = forms.CharField(
        max_length=12,
        required=False,
        help_text="Wenn Sie einen Einladungscode haben, geben Sie ihn hier ein."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2", "email", "language", "role")
        labels = {
            'first_name': "Vorname",
            'last_name': "Nachname",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # Берем текущий язык из системы и ставим его как начальный для поля language
        self.initial['language'] = translation.get_language()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        code = cleaned_data.get("invitation_code")

        if not code:
            return cleaned_data
        # Security by Obscurity
        error_generic = "Der Einladungscode oder die E-Mail-Adresse ist ungültig."
        error_expired = "Der Einladungscode ist abgelaufen."
        try:
            invitation = StudentInvitation.objects.get(code=code)
            if invitation.email == email:
                if invitation.is_used:
                    self.add_error('invitation_code', error_generic)
                elif invitation.is_expired():
                    self.add_error('invitation_code', error_expired)
                else:
                    pass
            else:
                self.add_error('invitation_code', error_generic)
        except StudentInvitation.DoesNotExist:
            self.add_error('invitation_code', error_generic)

        return cleaned_data

class ProfileForm(forms.ModelForm):
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
        required=False,
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
        }
        labels = {
            'email': _("E-Mail-Adresse des Studenten")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.expires_at:
                now = timezone.now()
                delta = self.instance.expires_at - now
                days_left = math.ceil(delta.total_seconds() / 86400)
                self.initial['days_valid'] = max(0, days_left)
        else:
            self.initial['days_valid'] = 7
