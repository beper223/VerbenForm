from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, DetailView, FormView, View, UpdateView, TemplateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy

from src.personal_forms.models import LearningUnit
from src.personal_forms.services import TrainingService, LearningUnitProgressService
from src.web.forms import RegistrationForm, UserSettingsForm
from src.users.models import User, StudentInvitation


class TeacherRequiredMixin:
    """
    Миксин для проверки прав учителя.
    Перенаправляет на страницу настроек профиля, если пользователь не является учителем.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher():
            return redirect('profile-settings')
        return super().dispatch(request, *args, **kwargs)


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


class DashboardView(LoginRequiredMixin, ListView):
    model = LearningUnit
    template_name = 'personal_forms/dashboard.html'
    context_object_name = 'units'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()
        units = LearningUnit.objects.order_by('order')

        # Получаем прогресс по всем юнитам одним махом (без N+1)
        context['units_overview'] = service.get_units_overview(self.request.user, units)
        context['stats'] = service.get_global_stats(self.request.user)
        return context


class TrainingSessionView(LoginRequiredMixin, DetailView):
    model = LearningUnit
    template_name = 'training/session.html'
    pk_url_kwarg = 'unit_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = TrainingService()
        unit = self.get_object()

        # Первая карточка при загрузке страницы
        card = service.get_next_card(
            user=self.request.user,
            learning_unit=unit,
            language=self.request.user.language
        )
        context['unit'] = unit
        context['card'] = card
        return context


class SubmitAnswerView(LoginRequiredMixin, View):
    """HTMX endpoint для обработки ответа и выдачи новой карточки"""

    def post(self, request):
        service = TrainingService()
        card_id = request.POST.get('card_id')
        user_answer = request.POST.get('answer')
        unit_id = request.POST.get('unit_id')

        unit = get_object_or_404(LearningUnit, id=unit_id)

        try:
            # 1. Проверяем ответ
            result = service.submit_answer(
                user=request.user,
                card_id=card_id,
                user_answer=user_answer
            )
        except ValueError:
            # Если карточка протухла, просто перезагружаем её
            return self._render_new_card(request, unit, service, None)

        return self._render_new_card(request, unit, service, result)

    @staticmethod
    def _render_new_card(request, unit, service, result):
        next_card = service.get_next_card(
            user=request.user,
            learning_unit=unit,
            language=request.user.language
        )
        if not next_card:
            return render(request, 'training/partials/finished.html')

        return render(request, 'training/partials/card_content.html', {
            'card': next_card,
            'unit': unit,
            'last_result': result
        })


class TeacherStudentsView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    template_name = 'teacher/students.html'

    def get_queryset(self):
        # Показываем только тех студентов, где текущий пользователь является учителем
        return self.request.user.students.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()
        students_data = []

        for student in self.get_queryset():
            students_data.append({
                'user': student,
                'stats': service.get_global_stats(student)
            })

        context['students_data'] = students_data
        return context

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