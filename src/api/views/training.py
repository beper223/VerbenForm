from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from dataclasses import asdict
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from src.personal_forms.models import LearningUnit
from src.personal_forms.services import TrainingService
from functools import cached_property


class TrainingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @cached_property
    def training_service(self):
        """Инициализируем сервис только при первом обращении"""
        return TrainingService()

    @action(detail=False, methods=["get"], url_path="next-card")
    def next_card(self, request):

        unit_id = request.query_params.get("learning_unit_id")
        if not unit_id:
            return Response({"detail": _("learning_unit_id erforderlich")}, status=status.HTTP_400_BAD_REQUEST)

        # Безопасное получение объекта
        unit = get_object_or_404(LearningUnit, id=unit_id)

        card = self.training_service.get_next_card(
            user=request.user,
            learning_unit=unit,
            language=request.user.language,
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
            return Response(asdict(result))
        except ValueError as e:
            # Например, "Card expired"
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

