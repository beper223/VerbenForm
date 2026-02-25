from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from src.personal_forms.models import LearningUnit, UserVerbProgress
from src.personal_forms.api.serializers import LearningUnitSerializer, UserVerbProgressSerializer
from src.personal_forms.services import TrainingService


class LearningUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Просмотр всех учебных модулей.
    """
    queryset = LearningUnit.objects.all().order_by("order")
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserVerbProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Просмотр прогресса пользователя.
    """
    serializer_class = UserVerbProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserVerbProgress.objects.filter(user=self.request.user)

class TrainingViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.training_service = TrainingService()

    @action(detail=False, methods=["get"])
    def next_card(self, request):

        unit_id = request.query_params.get("learning_unit_id")
        language = request.query_params.get("language", "en")

        if not unit_id:
            return Response({"detail": "learning_unit_id required"}, status=400)

        unit = LearningUnit.objects.get(id=unit_id)

        card = self.training_service.get_next_card(
            user=request.user,
            learning_unit=unit,
            language=language,
        )

        if not card:
            return Response({"detail": "No cards available"})

        return Response(card.__dict__)

    @action(detail=False, methods=["post"])
    def answer(self, request):

        try:
            result = self.training_service.submit_answer(
                user=request.user,
                card_id=request.data["card_id"],
                answer=request.data["answer"],
            )
        except ValueError:
            return Response({"detail": "Card expired"}, status=400)

        return Response(result.__dict__)