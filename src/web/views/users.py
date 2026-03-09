from django.contrib.auth.views import LoginView
from django.views.generic import FormView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import translation
from django.utils.translation import gettext_lazy as _


from src.web.forms import RegistrationForm, ProfileForm
from src.users.models import User, StudentInvitation



class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        lang = user.language or 'de'

        with translation.override(lang):
            if user.is_teacher():
                return reverse('web-teacher-dashboard')
            return reverse('units-list')

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

    def get_success_url(self):
        lang = self.object.language # Новый язык из базы
        with translation.override(lang):
            return reverse('web-profile')