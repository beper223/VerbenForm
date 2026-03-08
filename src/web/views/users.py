from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from src.web.forms import RegistrationForm, ProfileForm
from src.users.models import User, StudentInvitation



class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Определяет куда отправить пользователя после входа"""
        user = self.request.user
        if user.is_teacher():
            return reverse('web-teacher-dashboard')
        return reverse('units-list')

class UserLogoutView(LogoutView):
    # В Django 5.0+ LogoutView требует POST.
    # Если вы хотите разрешить GET, нужно переопределить dispatch (не рекомендуется)
    # или просто использовать POST в шаблоне.
    next_page = reverse_lazy('login')

class UserRegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        user = form.save()
        code = form.cleaned_data.get('invitation_code')

        if code:
            invite = StudentInvitation.objects.get(code=code, is_used=False)
            user.teachers.add(invite.teacher)
            invite.is_used = True
            invite.save()

        login(self.request, user)
        if user.is_teacher():
            return redirect('web-teacher-dashboard')
        return redirect('units-list')

class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'auth/profile.html'
    success_url = reverse_lazy('web-profile')
    success_message = _("Ihr Profil wurde erfolgreich aktualisiert!")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # Если язык изменился в профиле пользователя,
        # Django подхватит его из модели User при следующем запросе,
        # так как мы используем LocaleMiddleware и поле language в модели.
        response = super().form_valid(form)
        return response