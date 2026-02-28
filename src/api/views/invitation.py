from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from src.users.services import InvitationService
from src.users.permissions import IsTeacher


class InviteViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[IsTeacher])
    def get_invite(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": _("E-Mail-Adresse erforderlich")}, status=400)

        invitation = InvitationService.create_invitation(request.user, email)
        return Response({
            "detail": _("Einladung erstellt"),
            "code": invitation.code
        })

    @action(detail=False, methods=['post'], permission_classes=[IsTeacher])
    def invite_student(self, request):
        """Эндпоинт для учителя: отправляет инвайт на почту"""
        email = request.data.get("email")
        if not email:
            return Response({"detail": _("E-Mail-Adresse erforderlich")}, status=400)

        InvitationService.send_invitation(request.user, email)
        return Response({"detail": f"Invitation sent to {email}"})