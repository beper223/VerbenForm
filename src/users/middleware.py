from django.utils import translation


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            user_language = request.user.language
            # 2. Активируем язык из профиля пользователя
            translation.activate(user_language)
            # 3. Сообщаем Django, какой язык сейчас выбран
            request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)
        return response