from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, render
from django.views.generic import FormView, UpdateView, DeleteView
from django.contrib import messages
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
        # Берем дни, если пусто — ставим 7
        days = form.cleaned_data.get('days_valid') or 7
        expires_at = timezone.now() + timedelta(days=int(days))
        invitation = InvitationService.create_invitation(
            teacher=self.request.user,
            email=email,
            expires_at=expires_at
        )
        # Добавляем сообщение в систему Django Messages
        messages.success(
            self.request,
            f'Приглашение для {email} создано! Код: {invitation.code}',
            extra_tags='invitation'
        )

        if self.request.headers.get('HX-Request'):
            invitations = StudentInvitation.objects.filter(teacher=self.request.user).order_by('-created_at')
            return render(self.request, 'teacher/partials/invitation_list.html', {
                'invitations': invitations,
                'messages': messages.get_messages(self.request)  # Передаем свежие сообщения
            })
        return redirect('web-teacher-dashboard')

class InvitationUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = StudentInvitation
    form_class = InvitationForm
    template_name = 'teacher/partials/invitation_edit.html'  # Маленький шаблон для модалки или инлайна

    def form_valid(self, form):
        # Вычисляем новую дату от ТЕКУЩЕГО момента
        days = form.cleaned_data.get('days_valid') or 7
        form.instance.expires_at = timezone.now() + timedelta(days=int(days))

        messages.success(
            self.request,
            _("Das Ablaufdatum der Einladung wurde aktualisiert"),
            extra_tags='invitation'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('web-teacher-dashboard') + "?tab=invites"


class InvitationDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = StudentInvitation

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('HX-Request'):
            # Если запрос от HTMX, возвращаем пустой контент, чтобы строка удалилась из DOM
            return HttpResponse("")
        return redirect('web-teacher-dashboard')