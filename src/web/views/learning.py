from django.db.models import Q
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render

from src.personal_forms.models import LearningUnit, Course
from src.personal_forms.services import TrainingService, LearningUnitProgressService


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'personal_forms/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        user = self.request.user
        # Если админ — видит всё
        if user.is_staff:
            return Course.objects.all().order_by('-created_at')

        # Логика доступа: Публичные ИЛИ (Приватные и назначен ученику) ИЛИ (Автор курса)
        return Course.objects.filter(
            Q(visibility=Course.Visibility.PUBLIC) |
            Q(assigned_students=user) |
            Q(author=user)
        ).distinct().order_by('-created_at')


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'personal_forms/course_detail.html'
    pk_url_kwarg = 'course_id'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = LearningUnitProgressService()
        course = self.get_object()

        # 1. Получаем юниты только этого курса
        units = course.learning_units.all().order_by('order')

        # 2. Используем ваш сервис для расчета прогресса по этим юнитам
        context['units_overview'] = service.get_units_overview(self.request.user, list(units))

        # 3. Общая статистика пользователя (остается глобальной)
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

        # ПРОВЕРКА НА ЗАВЕРШЕНИЕ:
        # Если ответ верный и слово перешло в статус mastered (или уже было таким)
        if result.correct:
            # Проверяем, остались ли в этом юните невыученные слова
            progress_service = LearningUnitProgressService()
            unit_progress = progress_service.build_progress(user=request.user, learning_unit=unit)

            # Если все атомы выучены (completed=True)
            # И мы НЕ находимся в режиме "бесконечного повторения" (то есть мы только что закончили)
            # Мы можем проверить, был ли этот ответ "завершающим"
            if unit_progress['completed']:
                # Важно: показываем финиш, если юзер реально "добил" юнит.
                # Если он зашел в уже готовый юнит через "Wiederholen",
                # мы не будем показывать финиш после каждого ответа.
                # Для этого можно проверить, был ли streak именно пороговым (например 5)
                if result.streak == 5:  # Порог из вашего ProgressService.STREAK_TO_MASTER
                    return render(request, 'training/partials/finished.html', {'unit': unit, 'course': unit.course})

        return self._render_new_card(request, unit, service, result)

    @staticmethod
    def _render_new_card(request, unit, service, result):
        next_card = service.get_next_card(
            user=request.user,
            learning_unit=unit,
            language=request.user.language
        )
        if not next_card:
            return render(request, 'training/partials/finished.html', {
                'unit': unit,
                'course': unit.course
            })

        return render(request, 'training/partials/card_content.html', {
            'card': next_card,
            'unit': unit,
            'last_result': result
        })