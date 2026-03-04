from django import forms
from src.personal_forms.models import Course, LearningUnit

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CourseAssignmentForm(forms.ModelForm):
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
        # Используем Select2 или фильтры, если глаголов очень много