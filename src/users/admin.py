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
    filter_horizontal = ("teachers",)

    def is_teacher(self, obj):
        """Отображает в списке, является ли пользователь учителем"""
        return obj.groups.filter(name__in=["Teachers", "SuperTeachers"]).exists()

    is_teacher.boolean = True
    is_teacher.short_description = _("Lehrer")

    def get_teachers(self, obj):
        """Показывает список учителей ученика прямо в таблице"""
        return ", ".join([t.username for t in obj.teachers.all()])

    get_teachers.short_description = _("Lehrer")


@admin.register(StudentInvitation)
class StudentInvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "code", "teacher", "is_used", "created_at")
    list_filter = ("is_used", "teacher")
    search_fields = ("email", "code")
    readonly_fields = ("code", "created_at")  # Чтобы код нельзя было случайно изменить
