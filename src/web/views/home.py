from django.views.generic import TemplateView
from django.shortcuts import redirect

class HomeView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        # Если пользователь уже вошел, перекидываем его сразу в кабинет
        if request.user.is_authenticated:
            if request.user.is_teacher():
                return redirect('web-teacher-dashboard')
            return redirect('units-list')
        return super().dispatch(request, *args, **kwargs)