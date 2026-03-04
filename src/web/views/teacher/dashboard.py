from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from src.personal_forms.models import Course
from src.users.models import StudentInvitation

from src.personal_forms.services import LearningUnitProgressService
from src.web.forms import InvitationForm
from src.web.views.mixins import TeacherRequiredMixin


class TeacherDashboardView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    template_name = 'teacher/dashboard_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        service = LearningUnitProgressService()

        # Данные для вкладки 1: Курсы
        context['courses'] = Course.objects.filter(author=user).prefetch_related('learning_units')

        # Данные для вкладки 2: Приглашения
        context['invitations'] = StudentInvitation.objects.filter(teacher=user).order_by('-created_at')
        context['invite_form'] = InvitationForm()

        # Данные для вкладки 3: Ученики
        students = user.students.all()
        students_data = []
        for student in students:
            students_data.append({
                'user': student,
                'stats': service.get_global_stats(student)
            })
        context['students_data'] = students_data

        return context