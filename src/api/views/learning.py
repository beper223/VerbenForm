from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from src.personal_forms.models import LearningUnit, UserVerbProgress
from src.api.serializers import (
    LearningUnitSerializer,
    UserVerbProgressSerializer,
)

from src.personal_forms.services import LearningUnitProgressService

User = get_user_model()

class LearningUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LearningUnit.objects.all().order_by("order")
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        unit = self.get_object()

        target_user = request.user
        student_id = request.query_params.get('student_id')
        if student_id and request.user.groups.filter(name__in=['Teachers', 'SuperTeachers']).exists():
            target_user = get_object_or_404(User, id=student_id)

        service = LearningUnitProgressService()
        progress_data = service.build_progress(user=target_user, learning_unit=unit)
        return Response(progress_data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        service = LearningUnitProgressService()
        return Response(service.get_global_stats(request.user))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Определяем, чей прогресс смотрим (свой или ученика)
        target_user = request.user
        student_id = request.query_params.get('student_id')
        if student_id and request.user.groups.filter(name__in=['Teachers', 'SuperTeachers']).exists():
            target_user = get_object_or_404(User, id=student_id)

        service = LearningUnitProgressService()
        # Вызываем новый метод, который делает всё ОПТИМАЛЬНО
        data = service.get_units_overview(target_user, queryset)

        return Response(data)

class UserVerbProgressViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserVerbProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Если это учитель (из группы Teachers или SuperTeachers)
        if user.groups.filter(name__in=['Teachers', 'SuperTeachers']).exists():
            student_id = self.request.query_params.get('student_id')

            if student_id:
                # Учитель хочет посмотреть конкретного ученика.
                # Мы фильтруем: прогресс этого ученика И этот ученик привязан к учителю.
                return UserVerbProgress.objects.filter(
                    user_id=student_id,
                    user__teachers=user
                )

            # Если student_id не передан, учитель видит прогресс ВСЕХ своих учеников
            return UserVerbProgress.objects.filter(user__teachers=user)

        # Если это обычный ученик — он видит только себя
        return UserVerbProgress.objects.filter(user=user)