from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from src.web.forms import InvitationForm

from src.users.services import InvitationService
from src.web.views.mixins import TeacherRequiredMixin


class CreateInvitationView(LoginRequiredMixin, TeacherRequiredMixin, FormView):
    template_name = 'teacher/create_invitation.html'
    form_class = InvitationForm
    success_url = reverse_lazy('web-teacher-students')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        invitation = InvitationService.create_invitation(self.request.user, email)

        from django.contrib import messages
        messages.success(self.request, f'Приглашение создано. Код: {invitation.code}')
        return super().form_valid(form)