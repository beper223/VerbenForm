
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404

from src.personal_forms.models import LearningUnit
from src.personal_forms.services import LearningUnitProgressService
from src.users.models import User
from src.personal_forms.models import Course
from src.web.views.mixins import TeacherRequiredMixin


class StudentDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    """Список КУРСОВ ученика для учителя (аналог course_list.html)"""
    model = User
    template_name = 'teacher/student_course_list.html'
    pk_url_kwarg = 'student_id'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        service = LearningUnitProgressService()

        # 1. Получаем курсы, доступные ЭТОМУ студенту
        courses = Course.objects.filter(
            Q(visibility=Course.Visibility.PUBLIC)
            | (Q(assigned_students=student)
            & Q(author=self.request.user))
        ).distinct().order_by('-created_at')

        # 2. Рассчитываем прогресс по каждому курсу для этого студента
        courses_with_progress = []
        for course in courses:
            units = list(course.learning_units.all())
            overview = service.get_units_overview(student, units)

            # Считаем средний процент по курсу
            total_pct = sum(u['percent'] for u in overview) if overview else 0
            avg_pct = int(total_pct / len(overview)) if overview else 0

            courses_with_progress.append({
                'course': course,
                'percent': avg_pct,
                'unit_count': len(units)
            })

        context['courses_data'] = courses_with_progress
        context['global_stats'] = service.get_global_stats(student)
        return context


class StudentCourseDetailView(LoginRequiredMixin, TeacherRequiredMixin, DetailView):
    """Список ЮНИТОВ внутри курса для учителя (аналог course_detail.html)"""
    model = Course
    template_name = 'teacher/student_course_detail.html'
    pk_url_kwarg = 'course_id'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()

        # Получаем студента из URL
        student = get_object_or_404(User, id=self.kwargs['student_id'])
        course = self.get_object()

        # Юниты этого курса с прогрессом ЭТОГО студента
        units = list(course.learning_units.all().order_by('order'))
        context['units_overview'] = service.get_units_overview(student, units)
        context['student'] = student
        context['global_stats'] = service.get_global_stats(student)
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

        # Если в URL передан student_id, и текущий юзер - учитель, смотрим ученика
        student_id = self.request.GET.get('student_id')
        if student_id and self.request.user.is_teacher_admin():
            target_user = get_object_or_404(User, id=student_id)
            # Проверка связи учитель-ученик
            if (not self.request.user.is_staff
            and not target_user.teachers.filter(id=self.request.user.id).exists()):
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied()
        else:
            target_user = self.request.user

        # Строим прогресс только для этого юнита
        progress_data = service.build_progress(user=target_user, learning_unit=unit)

        # Добавляем все данные из словаря progress_data в контекст
        context.update(progress_data)
        context['target_user'] = target_user
        # Добавляем флаг, чтобы в шаблоне было проще сравнивать
        context['is_own_stats'] = (target_user == self.request.user)
        return context