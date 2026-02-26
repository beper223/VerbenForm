# src/personal_forms/api/views.py

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from dataclasses import asdict

from src.personal_forms.models import LearningUnit, UserVerbProgress
from src.personal_forms.api.serializers import LearningUnitSerializer, UserVerbProgressSerializer
from src.personal_forms.services import TrainingService, LearningUnitProgressService


class LearningUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LearningUnit.objects.all().order_by("order")
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        """
        Возвращает матрицу прогресса для конкретного юнита.
        GET /api/units/1/progress/
        """
        unit = self.get_object()
        service = LearningUnitProgressService()
        progress_data = service.build_progress(user=request.user, learning_unit=unit)
        return Response(progress_data)


class TrainingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализируем сервис один раз
        self.training_service = TrainingService()

    @action(detail=False, methods=["get"], url_path="next-card")
    def next_card(self, request):
        unit_id = request.query_params.get("learning_unit_id")
        language = request.query_params.get("language", "en")

        if not unit_id:
            return Response({"detail": "learning_unit_id required"}, status=status.HTTP_400_BAD_REQUEST)

        # Безопасное получение объекта
        unit = get_object_or_404(LearningUnit, id=unit_id)

        card = self.training_service.get_next_card(
            user=request.user,
            learning_unit=unit,
            language=language,
        )

        if not card:
            return Response({"detail": "No cards available in this unit"}, status=status.HTTP_204_NO_CONTENT)

        # Используем asdict для dataclass (чище чем __dict__)
        return Response(asdict(card))

    @action(detail=False, methods=["post"])
    def answer(self, request):
        card_id = request.data.get("card_id")
        user_answer = request.data.get("answer")

        if not card_id or user_answer is None:
            return Response({"detail": "card_id and answer are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = self.training_service.submit_answer(
                user=request.user,
                card_id=card_id,
                user_answer=user_answer,
            )
        except ValueError as e:
            # Например, "Card expired"
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(asdict(result))


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