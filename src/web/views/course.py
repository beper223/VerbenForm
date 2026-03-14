from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from src.personal_forms.models import Course
from src.web.forms import CourseForm, CourseAssignmentForm
from src.web.views.mixins import TeacherRequiredMixin


# CRUD для Курса
class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'teacher/courses/course_form.html'
    success_url = reverse_lazy('web-teacher-dashboard')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# Назначение курса студентам
class CourseAssignmentView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseAssignmentForm
    template_name = 'teacher/courses/assign_form.html'
    pk_url_kwarg = 'course_id'

    def get_success_url(self):
        # После сохранения состава возвращаемся к редактированию курса
        # return reverse_lazy('web-course-edit', kwargs={'pk': self.object.id})
        return reverse_lazy('web-teacher-dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user
        return kwargs

    def get_queryset(self):
        # Безопасность: менять состав можно только у своих курсов
        return self.model.objects.filter(author=self.request.user)

class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'teacher/courses/course_form.html'
    success_url = reverse_lazy('web-teacher-dashboard')

    def get_queryset(self):
        # Редактировать можно только свои курсы
        return self.model.objects.filter(author=self.request.user)

class CourseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('web-teacher-dashboard')

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)