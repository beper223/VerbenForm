from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.forms.models import BaseInlineFormSet
from django.db.models import Case, When, IntegerField
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

from src.personal_forms.models import Verb, VerbForm, VerbTranslation, LearningUnit
from src.common.choices import Tense, Pronoun, LanguageCode


# Константы для единого порядка везде
TENSE_ORDER = [Tense.PRAESENS.value, Tense.PRAETERITUM.value]
PRONOUN_ORDER = [p.value for p in Pronoun]
LANGUAGE_CODE_ORDER = LanguageCode.get_available_values()


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
    tense_value = Tense.PRAESENS.value

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

# --- ДВА РАЗНЫХ ИНЛАЙНА ---

class PraesensInline(BaseVerbFormInline):
    model = VerbForm
    verbose_name = "Präsens"
    verbose_name_plural = format_lazy("{}: {}", _("Konjugation"), "Präsens")
    tense_value = Tense.PRAESENS.value

class PraeteritumInline(BaseVerbFormInline):
    model = VerbForm # Используем Proxy модель!
    verbose_name = "Präteritum"
    verbose_name_plural = format_lazy("{}: {}", _("Konjugation"), "Präteritum")
    tense_value = Tense.PRAETERITUM.value


class VerbTranslationInlineModelForm(ModelForm):
    class Meta:
        model = VerbTranslation
        fields = ("language_code", "translation")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["translation"].required = False
        self.fields["language_code"].disabled = True


class VerbTranslationInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.forms.sort(key=self.get_form_sort_key)

    @staticmethod
    def get_form_sort_key(form):
        language_code = form.instance.language_code if form.instance.pk else form.initial.get("language_code")
        try:
            return LANGUAGE_CODE_ORDER.index(language_code)
        except (ValueError, KeyError):
            return 99

    @staticmethod
    def _should_save(form):
        return bool((form.cleaned_data.get("translation") or "").strip())

    def save_new(self, form, commit=True):
        if not self._should_save(form):
            return None

        instance = form.save(commit=False)
        setattr(instance, self.fk.name, self.instance)

        if not getattr(instance, "language_code", None):
            instance.language_code = form.initial.get("language_code")

        instance.translation = (form.cleaned_data.get("translation") or "").strip()

        if commit:
            instance.save()
        return instance

    def save_existing(self, form, instance, commit=True):
        if self._should_save(form):
            instance.translation = (form.cleaned_data.get("translation") or "").strip()
            if commit:
                instance.save(update_fields=["translation"])
            return instance

        if instance.pk:
            instance.delete()
        return None


class VerbTranslationInline(admin.TabularInline):
    model = VerbTranslation
    form = VerbTranslationInlineModelForm
    formset = VerbTranslationInlineFormSet
    can_delete = False
    fields = ("language_code", "translation")
    extra = 0

    def get_extra(self, request, obj=None, **kwargs):
        if not obj:
            return len(LANGUAGE_CODE_ORDER)
        existing_count = obj.translations.count()
        return max(0, len(LANGUAGE_CODE_ORDER) - existing_count)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        whens = [When(language_code=code, then=i) for i, code in enumerate(LANGUAGE_CODE_ORDER)]
        return qs.annotate(sort_id=Case(*whens, output_field=IntegerField())).order_by("sort_id")

    def get_formset(self, request, obj=None, **kwargs):
        form_set = super().get_formset(request, obj, **kwargs)
        existing = [] if not obj else list(obj.translations.values_list("language_code", flat=True))
        missing_data = [{"language_code": code} for code in LANGUAGE_CODE_ORDER if code not in existing]

        class CustomFormSet(form_set):
            def __init__(self, *args, **inner_kwargs):
                if not args and "initial" not in inner_kwargs:
                    inner_kwargs["initial"] = missing_data
                super().__init__(*args, **inner_kwargs)

        return CustomFormSet

@admin.register(Verb)
class VerbAdmin(admin.ModelAdmin):
    list_display = (
        "infinitive",
        "level",
        "verb_type",
        "reflexivitaet",
        "is_trennbare",
        "case",
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
    list_per_page = 20

    inlines = [PraesensInline, PraeteritumInline, VerbTranslationInline]

    fieldsets = (
        (_("Grundform"), {
            "fields": (
                "infinitive",
                "level",
                "verb_type",
                "reflexivitaet",
                "is_trennbare",
                "case"
            )
        }),
        (_("Perfekt"), {
            "fields": ("auxiliary", "participle_ii"),
            "description": _("Nur für Perfekt erforderlich"),
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
    list_per_page = 6


@admin.register(VerbTranslation)
class VerbTranslationAdmin(admin.ModelAdmin):
    list_display = (
        "verb",
        "language_code",
        "translation",
    )
    list_filter = (
        "language_code",
    )
    search_fields = (
        "verb__infinitive",
        "translation",
    )
    list_per_page = 20

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
    list_per_page = 20

    filter_horizontal = ("verbs",)
