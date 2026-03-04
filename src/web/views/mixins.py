from django.shortcuts import redirect

class TeacherRequiredMixin:
    """
    Миксин для проверки прав учителя.
    Перенаправляет на страницу настроек профиля, если пользователь не является учителем.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher_admin():
            return redirect('profile-settings')
        return super().dispatch(request, *args, **kwargs)