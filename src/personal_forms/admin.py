from typing import List, Dict
from typing import Optional, Type

from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from src.personal_forms.models import Verb, VerbForm, LearningUnit
from src.common.choices import Tense, Pronoun


class VerbFormInlineFormSet(BaseInlineFormSet):


    def save_new(self, form, commit=True):
        # сохраняем только если поле form заполнено
        if form.cleaned_data.get("form"):
            return super().save_new(form, commit=commit)
        return None

    def save_existing(self, form, instance, commit=True):
        # если поле form заполнено — сохраняем
        if form.cleaned_data.get("form"):
            return super().save_existing(form, instance, commit=commit)

        # если очищено — удаляем объект
        if instance.pk:
            instance.delete()
        return None

class VerbFormInline(admin.TabularInline):
    model = VerbForm
    formset = VerbFormInlineFormSet
    extra = 0
    can_delete = True
    fields = ("tense", "pronoun", "form")

    # Сортировка существующих VerbForm
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # сортируем по tense и по порядку местоимений
        pronoun_order = [p.value for p in Pronoun]

        # Простой способ сортировки: сначала Präsens, потом Präteritum
        tense_sort = {"Präsens": 0, "Präteritum": 1}

        # Сортируем в Python, а не через Case/When
        qs = sorted(
            qs,
            key=lambda x: (tense_sort[x.tense], pronoun_order.index(x.pronoun))
        )

        return qs

    def get_formset(self, request, obj: Optional[Verb] = None, **kwargs)-> Type[BaseInlineFormSet]:
        all_combinations = [
            (tense.value, pronoun.value)
            for tense in (Tense.PRAESENS, Tense.PRAETERITUM)
            for pronoun in Pronoun
        ]

        # СОЗДАНИЕ НОВОГО VERB
        if obj is None:
            kwargs["extra"] = len(all_combinations)
            kwargs["initial"] = [
                {"tense": tense, "pronoun": pronoun}
                for tense, pronoun in all_combinations
            ]
            return super().get_formset(request, obj, **kwargs)

        # РЕДАКТИРОВАНИЕ СУЩЕСТВУЮЩЕГО VERB

        # Получаем уже существующие формы
        existing = set(
            obj.forms.values_list("tense", "pronoun")
        )

        # Вычисляем недостающие комбинации
        missing = [
            (tense, pronoun)
            for tense, pronoun in all_combinations
            if (tense, pronoun) not in existing
        ]

        kwargs["extra"] = len(missing)
        kwargs["initial"] = [
            {"tense": tense, "pronoun": pronoun}
            for tense, pronoun in missing
        ]

        return super().get_formset(request, obj, **kwargs)

    # Ограничиваем выбор tense в Inline, убираем Perfekt
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "tense":
            # Берём только Präsens и Präteritum
            kwargs["choices"] = [
                (Tense.PRAESENS.value, Tense.PRAESENS.value),
                (Tense.PRAETERITUM.value, Tense.PRAETERITUM.value)
            ]
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
