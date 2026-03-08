from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from src.personal_forms.models import Course, LearningUnit

User = get_user_model()

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CourseAssignmentForm(forms.ModelForm):
    assigned_students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # По умолчанию пусто
        widget=forms.CheckboxSelectMultiple,
        label=_("Kursteilnehmer (Ihre Studenten)"),
        required=False
    )

    class Meta:
        model = Course
        fields = ['assigned_students']
        widgets = {
            'assigned_students': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            # Учитель может назначать курс только своим ученикам
            self.fields['assigned_students'].queryset = teacher.students.all()

class UnitForm(forms.ModelForm):
    class Meta:
        model = LearningUnit
        fields = ['course', 'title', 'level', 'skill_type', 'order', 'verbs']
        widgets = {
            # Оставляем курс выпадающим списком, но отфильтруем его в __init__
            'course': forms.Select(attrs={'class': 'form-select'}),
            # Используем обычный селект, Tom Select превратит его в продвинутый поиск
            'verbs': forms.SelectMultiple(attrs={'id': 'verb-select'}),
        }
    def __init__(self, *args, **kwargs):
        # Можно передать пользователя в форму, если нужно отфильтровать список курсов
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(author=user)
            # Сортируем глаголы по алфавиту для удобства поиска
        self.fields['verbs'].queryset = self.fields['verbs'].queryset.order_by('infinitive')
