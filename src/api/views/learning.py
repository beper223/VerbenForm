from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied # Для конвертации ошибки сервиса в 403

from src.api.mixins import StudentAccessMixin
from src.personal_forms.models import LearningUnit, UserVerbProgress
from src.api.serializers import (
    LearningUnitSerializer,
    UserVerbProgressSerializer,
)

from src.personal_forms.services import LearningUnitProgressService


User = get_user_model()

class LearningUnitViewSet(StudentAccessMixin, viewsets.ReadOnlyModelViewSet):
    queryset = LearningUnit.objects.all().order_by("order")
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_progress_service(self):
        """Хелпер для получения инстанса сервиса"""
        return LearningUnitProgressService()

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        unit = self.get_object()
        service = self._get_progress_service()
        #  Используем метод из Mixin! Он сам сделает try/except и выкинет 403 если надо
        target_user = self.get_authorized_target_user()
        progress_data = service.build_progress(user=target_user, learning_unit=unit)
        return Response(progress_data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Глобальная статистика текущего пользователя"""
        service = LearningUnitProgressService()
        return Response(service.get_global_stats(request.user))

    def list(self, request, *args, **kwargs):
        # Метод пришел из Mixin!
        target_user = self.get_authorized_target_user()
        service = self._get_progress_service()
        data = service.get_units_overview(target_user, self.get_queryset())
        return Response(data)

class UserVerbProgressViewSet(StudentAccessMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = UserVerbProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Метод пришел из Mixin!
        target_user = self.get_authorized_target_user()
        return UserVerbProgress.objects.filter(user=target_user)