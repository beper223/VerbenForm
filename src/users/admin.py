from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from src.users.models import User, StudentInvitation


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Что отображать в списке пользователей
    list_display = ("username", "email", "get_teachers", "language", "is_staff", "is_teacher")
    list_filter = ("groups", "is_staff", "is_superuser", "language")

    # Добавляем наши поля в формы редактирования
    # fieldsets управляет страницей редактирования
    fieldsets = UserAdmin.fieldsets + (
        (_("Weitere Informationen"), {"fields": ("language", "teachers")}),
    )

    # Для создания пользователя (если нужно через админку)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("Weitere Informationen"), {"fields": ("language", "teachers")}),
    )

    # Удобный интерфейс выбора учителей (множественный выбор с поиском)
    filter_horizontal = ("teachers", "groups", "user_permissions",)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Если не суперпользователь - скрываем права и группы
        if not request.user.is_superuser:
            new_fieldsets = []
            for title, info in fieldsets:
                # Убираем разделы, содержащие поля прав доступа
                if 'groups' in info['fields'] or 'user_permissions' in info['fields']:
                    continue
                # Убираем раздел с датами
                if 'last_login' in info['fields'] or 'date_joined' in info['fields']:
                    continue
                new_fieldsets.append((title, info))
            return new_fieldsets

            # Суперпользователь видит ВСЁ (включая стандартный раздел Permissions с группами)
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined'
        return super().get_readonly_fields(request, obj)

    def is_teacher(self, obj):
        """Отображает в списке, является ли пользователь учителем"""
        return obj.groups.filter(name__in=["Teachers", "SuperTeachers"]).exists()

    is_teacher.boolean = True
    is_teacher.short_description = _("Lehrer")

    def get_teachers(self, obj):
        """Показывает список учителей ученика прямо в таблице"""
        return ", ".join([t.username for t in obj.teachers.all()])

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Если имя поля 'language', меняем виджет на RadioSelect
        if db_field.name == 'language':
            kwargs['widget'] = forms.RadioSelect
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    get_teachers.short_description = _("Lehrer")


@admin.register(StudentInvitation)
class StudentInvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "code", "teacher", "is_used", "created_at")
    list_filter = ("is_used", "teacher")
    search_fields = ("email", "code")
    readonly_fields = ("code", "created_at")  # Чтобы код нельзя было случайно изменить
