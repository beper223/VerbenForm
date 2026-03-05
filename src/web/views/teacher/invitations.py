from django.shortcuts import redirect, render
from django.views.generic import FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse

from src.web.forms import InvitationForm

from src.users.services import InvitationService
from src.web.views.mixins import TeacherRequiredMixin
from src.users.models import StudentInvitation


class CreateInvitationView(LoginRequiredMixin, TeacherRequiredMixin, FormView):
    template_name = 'teacher/create_invitation.html'
    form_class = InvitationForm
    # success_url = reverse_lazy('web-teacher-students')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        expires_at = form.cleaned_data['expires_at']
        # invitation = InvitationService.create_invitation(self.request.user, email)
        InvitationService.create_invitation(
            teacher=self.request.user,
            email=email,
            expires_at=expires_at
        )
        # from django.contrib import messages
        # messages.success(self.request, f'Приглашение создано. Код: {invitation.code}')
        # return super().form_valid(form)
        # Если это HTMX запрос, возвращаем обновленный список
        if self.request.headers.get('HX-Request'):
            invitations = StudentInvitation.objects.filter(teacher=self.request.user).order_by('-created_at')
            return render(self.request, 'teacher/partials/invitation_list.html', {'invitations': invitations})
        return redirect('web-teacher-dashboard')

class InvitationUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = StudentInvitation
    form_class = InvitationForm
    template_name = 'teacher/partials/invitation_edit.html'  # Маленький шаблон для модалки или инлайна

    def get_success_url(self):
        return reverse_lazy('web-teacher-dashboard')


class InvitationDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = StudentInvitation

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('HX-Request'):
            # Если запрос от HTMX, возвращаем пустой контент, чтобы строка удалилась из DOM
            return HttpResponse("")
        return redirect('web-teacher-dashboard')