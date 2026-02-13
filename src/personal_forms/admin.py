from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.forms.models import BaseInlineFormSet
from django.db.models import Case, When, IntegerField

from src.personal_forms.models import Verb, VerbForm, LearningUnit
from src.common.choices import Tense, Pronoun


# Константы для единого порядка везде
TENSE_ORDER = [Tense.PRAESENS.value, Tense.PRAETERITUM.value]
PRONOUN_ORDER = [p.value for p in Pronoun]


class VerbFormInlineModelForm(ModelForm):
    class Meta:
        model = VerbForm
        fields = ("tense", "pronoun", "form")
        widgets = {"tense": HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pronoun"].required = False
        self.fields["form"].required = False
        self.fields["pronoun"].disabled = True

class VerbFormInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            # Сортируем формы по местоимению перед отрисовкой
            self.forms.sort(key=self.get_form_sort_key)

    @staticmethod
    def get_form_sort_key(form):
        # Определяем значения для сортировки (из БД или из initial)
        pronoun = form.instance.pronoun if form.instance.pk else form.initial.get("pronoun")
        try:
            return PRONOUN_ORDER.index(pronoun)
        except (ValueError, KeyError):
            return 99

    @staticmethod
    def _should_save(form):
        return bool(form.cleaned_data.get("form"))

    def save_new(self, form, commit=True):
        return super().save_new(form, commit) if self._should_save(form) else None

    def save_existing(self, form, instance, commit=True):
        if self._should_save(form):
            return super().save_existing(form, instance, commit)
        if instance.pk:
            instance.delete()
        return None

class BaseVerbFormInline(admin.TabularInline):
    model = VerbForm
    form = VerbFormInlineModelForm
    formset = VerbFormInlineFormSet
    can_delete = False
    fields = ("pronoun", "form")
    extra = 0

    def get_queryset(self, request):
        # Сортировка внутри каждой группы только по местоимению
        qs = super().get_queryset(request).filter(tense=self.tense_value)
        pronoun_order = [p.value for p in Pronoun]
        whens = [When(pronoun=p, then=i) for i, p in enumerate(pronoun_order)]
        return qs.annotate(sort_id=Case(*whens, output_field=IntegerField())).order_by("sort_id")

    def get_extra(self, request, obj=None, **kwargs):
        if not obj: return 6
        existing_count = obj.forms.filter(tense=self.tense_value).count()
        return max(0, 6 - existing_count)

    def get_formset(self, request, obj=None, **kwargs):
        form_set = super().get_formset(request, obj, **kwargs)
        # Генерируем начальные данные только для конкретного времени
        existing = [] if not obj else list(obj.forms.filter(tense=self.tense_value).values_list("pronoun", flat=True))
        missing_data = [{"pronoun": p, "tense": self.tense_value} for p in PRONOUN_ORDER if p not in existing]

        class CustomFormSet(form_set):
            def __init__(self, *args, **inner_kwargs):
                if not args and 'initial' not in inner_kwargs:
                    inner_kwargs['initial'] = missing_data
                super().__init__(*args, **inner_kwargs)

            # Автоматически проставляем нужное время при сохранении новых форм
            def save_new(self, form, commit=True):
                if not self._should_save(form):
                    return None
                instance = form.save(commit=False)
                setattr(instance, self.fk.name, self.instance)
                instance.tense = self.instance_tense_value  # передаем из инлайна
                if commit:
                    instance.save()
                return instance

        CustomFormSet.instance_tense_value = self.tense_value
        return CustomFormSet



class PraesensVerbForm(VerbForm):
    class Meta:
        proxy = True  # Это не создает новую таблицу, просто дает Django "псевдоним"
        verbose_name = "Form (Präsens)"
        verbose_name_plural = "Konjugation: Präsens"

class PraeteritumVerbForm(VerbForm):
    class Meta:
        proxy = True  # Это не создает новую таблицу, просто дает Django "псевдоним"
        verbose_name = "Form (Präteritum)"
        verbose_name_plural = "Konjugation: Präteritum"

# --- ДВА РАЗНЫХ ИНЛАЙНА ---

class PraesensInline(BaseVerbFormInline):
    model = PraesensVerbForm
    verbose_name = "Präsens"
    verbose_name_plural = "Konjugation: Präsens"
    tense_value = Tense.PRAESENS.value

class PraeteritumInline(BaseVerbFormInline):
    model = PraeteritumVerbForm # Используем Proxy модель!
    verbose_name = "Präteritum"
    verbose_name_plural = "Konjugation: Präteritum"
    tense_value = Tense.PRAETERITUM.value

@admin.register(Verb)
class VerbAdmin(admin.ModelAdmin):
    list_display = (
        "infinitive",
        "level",
        "verb_type",
        "auxiliary",
        "participle_ii",
    )

    list_filter = (
        "level",
        "verb_type",
        "auxiliary",
    )

    search_fields = (
        "infinitive",
        "participle_ii",
    )

    ordering = ("infinitive",)

    inlines = [PraesensInline, PraeteritumInline] #[VerbFormInline]

    fieldsets = (
        ("Grundform", {
            "fields": ("infinitive", "level", "verb_type")
        }),
        ("Perfekt", {
            "fields": ("auxiliary", "participle_ii"),
            "description": "Nur für Perfekt erforderlich",
        }),
    )

# Полезно для массовой проверки / фильтрации.
@admin.register(VerbForm)
class VerbFormAdmin(admin.ModelAdmin):
    list_display = (
        "verb",
        "tense",
        "pronoun",
        "form",
    )

    list_filter = (
        "tense",
        "pronoun",
    )

    search_fields = (
        "verb__infinitive",
        "form",
    )

    ordering = (
        "verb__infinitive",
        "tense",
        "pronoun",
    )

@admin.register(LearningUnit)
class LearningUnitAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "level",
        "tense",
        "order",
    )

    list_filter = (
        "level",
        "tense",
    )

    ordering = ("order",)

    filter_horizontal = ("verbs",)
