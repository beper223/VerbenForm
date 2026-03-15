import json
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from src.personal_forms.models import Course, LearningUnit

User = get_user_model()

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'visibility']
        # widgets = {
        #     'description': forms.Textarea(attrs={'rows': 3}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Получаем текущие значения из JSON
        try:
            current_data = json.loads(self.instance.description or '{}')
        except ValueError:
            current_data = {}

        # Динамически создаем поля для каждого языка в форме
        for lang_code, lang_name in settings.LANGUAGES:
            field_name = f'desc_{lang_code}'
            self.fields[field_name] = forms.CharField(
                label="",#_("Beschreibung") + f" ({lang_name})",
                widget=forms.Textarea(attrs={
                    'rows': 4,
                    'class': 'form-control',  # Явно добавляем класс
                    'placeholder': _("Kursbeschreibung eingeben...")
                }),
                initial=current_data.get(lang_code, ''),
                required=False
            )

        # Скрываем основное поле description, так как мы будем собирать его из desc_...
        self.fields['description'].widget = forms.HiddenInput()
        self.fields['description'].required = False

    def clean(self):
        cleaned_data = super().clean()
        description_json = {}

        # Собираем данные из всех языковых полей в один словарь
        for lang_code, _ in settings.LANGUAGES:
            field_name = f'desc_{lang_code}'
            value = cleaned_data.get(field_name)
            if value:
                description_json[lang_code] = value

        # Записываем JSON-строку в основное поле
        cleaned_data['description'] = json.dumps(description_json, ensure_ascii=False)
        return cleaned_data

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
