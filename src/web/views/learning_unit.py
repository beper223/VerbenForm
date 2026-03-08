from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse

from src.personal_forms.models import Course, LearningUnit, Verb
from src.web.forms import UnitForm
from src.web.views.mixins import TeacherRequiredMixin

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем учителя в форму
        return kwargs

class UnitUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = LearningUnit
    form_class = UnitForm
    template_name = 'teacher/units/unit_form.html'
    success_url = reverse_lazy('web-teacher-dashboard')

    def get_queryset(self):
        # Только юниты в курсах, где пользователь — автор
        return self.model.objects.filter(course__author=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем учителя в форму
        return kwargs

class UnitDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = LearningUnit
    success_url = reverse_lazy('web-teacher-dashboard')

    # Если запрос пришел через HTMX, мы можем вернуть пустой ответ или статус 200
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('HX-Request'):
            # Возвращаем пустой ответ. HTMX увидит статус 200
            # и удалит элемент, который мы указали в hx-target
            from django.http import HttpResponse
            return HttpResponse("")
        return redirect(self.get_success_url())

class VerbLookupView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        query = request.GET.get('q', '')
        if len(query) < 2:  # Начинаем поиск от 2-х символов
            return JsonResponse({'results': []})

        verbs = Verb.objects.filter(infinitive__icontains=query).order_by('infinitive')[:20]
        results = [{'id': v.id, 'text': v.infinitive} for v in verbs]
        return JsonResponse({'results': results})