from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from src.personal_forms.models import Verb, VerbForm, LearningUnit
from src.common.choices import Tense, Pronoun


# Константы для единого порядка везде
TENSE_ORDER = [Tense.PRAESENS.value, Tense.PRAETERITUM.value]
PRONOUN_ORDER = [p.value for p in Pronoun]

class VerbFormInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            # Сортируем формы по времени и местоимению перед отрисовкой
            self.forms.sort(key=self.get_form_sort_key)

    @staticmethod
    def get_form_sort_key(form):
        # Определяем значения для сортировки (из БД или из initial)
        val = (form.instance.tense, form.instance.pronoun) if form.instance.pk \
               else (form.initial.get('tense'), form.initial.get('pronoun'))
        try:
            return TENSE_ORDER.index(val[0]), PRONOUN_ORDER.index(val[1])
        except (ValueError, KeyError):
            return 99, 99

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

class VerbFormInline(admin.TabularInline):
    model = VerbForm
    formset = VerbFormInlineFormSet
    can_delete = True
    fields = ("tense", "pronoun", "form")
    extra = 0

    @staticmethod
    def get_missing_forms(obj):
        full_set = [{"tense": t, "pronoun": p} for t in TENSE_ORDER for p in PRONOUN_ORDER]
        if not obj: return full_set
        existing = set(obj.forms.values_list("tense", "pronoun"))
        return [f for f in full_set if (f["tense"], f["pronoun"]) not in existing]

    def get_extra(self, request, obj=None, **kwargs):
        return len(self.get_missing_forms(obj))

    def get_formset(self, request, obj=None, **kwargs):
        form_set = super().get_formset(request, obj, **kwargs)
        missing_data = self.get_missing_forms(obj)

        class VerbFormDefaultInitialFormSet(form_set):
            def __init__(self, *args, **inner_kwargs):
                if not args and 'initial' not in inner_kwargs:
                    inner_kwargs['initial'] = missing_data
                super().__init__(*args, **inner_kwargs)
        return VerbFormDefaultInitialFormSet

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name in ["tense", "pronoun"]:
            kwargs["disabled"] = True  # Это делает поля недоступными для редактирования

        if db_field.name == "tense":
            kwargs["choices"] = [(t, t) for t in TENSE_ORDER]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

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

    inlines = [VerbFormInline]

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
