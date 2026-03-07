
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from src.personal_forms.models import LearningUnit
from src.personal_forms.services import LearningUnitProgressService
from src.users.models import User
from src.web.views.mixins import TeacherRequiredMixin


class StudentDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    model = User
    template_name = 'teacher/student_detail.html'
    pk_url_kwarg = 'student_id'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()

        # 1. Проверяем, имеет ли текущий пользователь право смотреть этого студента
        try:
            student = service.get_authorized_user(self.request.user, str(self.kwargs['student_id']))
        except PermissionError:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Keна права доступа к этому ученику.")

        # 2. Получаем все уроки
        units = LearningUnit.objects.order_by('order')

        # 3. Для каждого урока строим детальную матрицу прогресса
        units_data = []
        for unit in units:
            progress_data = service.build_progress(user=student, learning_unit=unit)
            units_data.append({
                'unit': unit,
                'matrix': progress_data['matrix'],  # Глаголы и их статусы
                'percent': progress_data['percent'],
                'mastered_atoms': progress_data['mastered_atoms'],
                'total_atoms': progress_data['total_atoms'],
            })

        context['units_data'] = units_data
        context['global_stats'] = service.get_global_stats(student)
        return context

class StudentStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'teacher/student_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()
        context['student'] = self.request.user
        context['own_stats'] = True  # Флаг что это просмотр собственной статистики

        # 1. Получаем все уроки
        units = LearningUnit.objects.order_by('order')

        # 2. Для каждого урока строим детальную матрицу прогресса для текущего студента
        units_data = []
        for unit in units:
            progress_data = service.build_progress(user=self.request.user, learning_unit=unit)
            units_data.append({
                'unit': unit,
                'matrix': progress_data['matrix'],  # Глаголы и их статусы
                'percent': progress_data['percent'],
                'mastered_atoms': progress_data['mastered_atoms'],
                'total_atoms': progress_data['total_atoms'],
            })

        context['units_data'] = units_data
        context['global_stats'] = service.get_global_stats(self.request.user)
        return context

class UnitStatsView(LoginRequiredMixin, DetailView):
    model = LearningUnit
    template_name = 'personal_forms/unit_stats.html'
    pk_url_kwarg = 'unit_id'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()
        unit = self.get_object()

        # Строим прогресс только для этого юнита
        progress_data = service.build_progress(user=self.request.user, learning_unit=unit)

        # Добавляем все данные из словаря progress_data в контекст
        context.update(progress_data)
        context['stats'] = service.get_global_stats(self.request.user)
        return context