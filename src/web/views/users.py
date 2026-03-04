from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

from src.web.forms import RegistrationForm, UserSettingsForm
from src.users.models import User, StudentInvitation



class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
    # В Django 5.0+ LogoutView требует POST.
    # Если вы хотите разрешить GET, нужно переопределить dispatch (не рекомендуется)
    # или просто использовать POST в шаблоне.
    next_page = reverse_lazy('login')

class UserRegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('units-list')

    def form_valid(self, form):
        user = form.save()
        code = form.cleaned_data.get('invitation_code')

        if code:
            try:
                invite = StudentInvitation.objects.get(code=code, is_used=False)
                user.teachers.add(invite.teacher)
                invite.is_used = True
                invite.save()
            except StudentInvitation.DoesNotExist:
                pass  # Или добавить ошибку в form

        login(self.request, user)
        return redirect(self.success_url)

class ProfileSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsForm
    template_name = 'profile/settings.html'
    success_url = reverse_lazy('profile-settings')
    success_message = "Ваш профиль успешно обновлен!"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # Если язык изменился в профиле пользователя,
        # Django подхватит его из модели User при следующем запросе,
        # так как мы используем LocaleMiddleware и поле language в модели.
        response = super().form_valid(form)
        return response