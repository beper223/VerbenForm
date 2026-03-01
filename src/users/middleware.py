from django.utils import translation


class UserLanguageMiddleware:
    # 1. Проверяет авторизацию - работает только для request.user.is_authenticated
    # 2. Получает язык пользователя - из поля request.user.language
    # 3. Активирует язык - через translation.activate(user_language)
    # 4. Устанавливает LANGUAGE_CODE - в request.LANGUAGE_CODE для Django
    # Результат: Авторизованные пользователи видят интерфейс на языке, указанном в их профиле,
    # без необходимости вручную переключать язык каждый раз.
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Проверяем, авторизован ли пользователь
        # print(f"DEBUG:")
        if request.user.is_authenticated:
            user_language = request.user.language
            # 2. Активируем язык из профиля пользователя
            translation.activate(user_language)
            # DEBUG
            # print(f"DEBUG: Activating language '{user_language}' for user '{request.user.username}'")
            # 3. Сообщаем Django, какой язык сейчас выбран
            request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)
        return response