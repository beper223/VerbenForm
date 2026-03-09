from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

# Технические маршруты (без префиксов)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('src.api.urls')),
]

# Маршруты сайта и админки (с префиксами /ru/, /de/ ...)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('src.web.urls')),
    prefix_default_language=True, # Опционально: True добавит префикс даже для языка по умолчанию
)