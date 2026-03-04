from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect

from src.personal_forms.models import Course, LearningUnit
from src.web.forms import UnitForm
from web.views.mixins import TeacherRequiredMixin

class UnitCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = LearningUnit
    form_class = UnitForm
    template_name = 'teacher/units/unit_form.html'
    success_url = reverse_lazy('web-teacher-dashboard')

    def get_initial(self):
        initial = super().get_initial()
        course_id = self.kwargs.get('course_id')
        if course_id:
            initial['course'] = get_object_or_404(Course, id=course_id, author=self.request.user)
        return initial


class UnitUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = LearningUnit
    form_class = UnitForm
    template_name = 'teacher/units/unit_form.html'
    success_url = reverse_lazy('web-teacher-dashboard')

    def get_queryset(self):
        # Только юниты в курсах, где пользователь — автор
        return self.model.objects.filter(course__author=self.request.user)


class UnitDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = LearningUnit
    success_url = reverse_lazy('web-teacher-dashboard')

    # Если запрос пришел через HTMX, мы можем вернуть пустой ответ или статус 200
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('HX-Request'):
            return render(request, 'teacher/partials/empty.html')  # Просто удаляем элемент из DOM
        return redirect(self.get_success_url())