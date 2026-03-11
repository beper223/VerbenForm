from django.views.generic import TemplateView

class ImpressumView(TemplateView):
    template_name = 'legal/impressum.html'

class PrivacyView(TemplateView):
    template_name = 'legal/privacy.html'