from rest_framework import permissions

class IsSuperTeacher(permissions.BasePermission):
    """Опытные преподаватели (могут править контент)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='SuperTeachers').exists()

class IsTeacher(permissions.BasePermission):
    """Все преподаватели (могут регистрировать учеников)"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_teacher_admin())
        #         and (
        #     request.user.groups.filter(name='Teachers').exists() or
        #     request.user.groups.filter(name='SuperTeachers').exists()
        # ))