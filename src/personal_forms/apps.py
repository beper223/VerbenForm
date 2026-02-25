from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PersonalFormsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.personal_forms'
    verbose_name = _("Personalformen")

    def ready(self):
        import src.personal_forms.signals
