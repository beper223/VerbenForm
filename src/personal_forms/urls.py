from django.http import JsonResponse
from django.urls import path, include
from src.personal_forms.api.views import LearningUnitViewSet, UserVerbProgressViewSet
from rest_framework.routers import DefaultRouter

# Создаем роутер для ViewSet'ов
router = DefaultRouter()
router.register(r'learning-units', LearningUnitViewSet, basename='learning-unit')
router.register(r'verb-progress', UserVerbProgressViewSet, basename='verb-progress')

# Тестовый view для проверки
def test_api(request):
    return JsonResponse({
        'message': 'API работает!',
        'status': 'success',
        'endpoints': [
            '/api/test/',
            '/api/learning-units/',
            '/api/verb-progress/',
        ]
    })

urlpatterns = [
    # Тестовый эндпоинт
    path('test/', test_api, name='api-test'),
    
    # API эндпоинты через роутер
    path('', include(router.urls)),
]