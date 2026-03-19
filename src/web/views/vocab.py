from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import HttpResponse

from src.personal_forms.models import VerbGroup
from src.web.forms import VerbGroupForm
from src.web.views.mixins import TeacherRequiredMixin

class VerbGroupCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = VerbGroup
    form_class = VerbGroupForm
    template_name = 'teacher/verbs/group_form.html'

    def get_success_url(self):
        return reverse('web-teacher-dashboard') + "?tab=vocab"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class VerbGroupUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = VerbGroup
    form_class = VerbGroupForm
    template_name = 'teacher/verbs/group_form.html'

    def get_success_url(self):
        return reverse('web-teacher-dashboard') + "?tab=vocab"

    def get_queryset(self):
        return self.model.objects.filter(course__author=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class VerbGroupDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = VerbGroup

    def get_queryset(self):
        return self.model.objects.filter(course__author=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse("")  # HTMX удалит строку из таблицы
        return redirect(reverse('web-teacher-dashboard') + "?tab=vocab")