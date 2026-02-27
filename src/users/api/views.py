from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from src.users.models import StudentInvitation
from src.users.services import InvitationService
from src.users.permissions import IsTeacher

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):

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

    @action(detail=False, methods=['post'], permission_classes=[])  # AllowAny
    def activate_student(self, request):
        """Эндпоинт для ученика: первый вход по коду"""
        code = request.data.get("code")
        username = request.data.get("username")
        password = request.data.get("password")

        invitation = get_object_or_404(StudentInvitation, code=code, is_used=False)

        # 1. Проверяем, существует ли уже такой пользователь
        user = User.objects.filter(email=invitation.email).first()

        if user:
            # Если пользователь уже есть (другой учитель его приглашал раньше)
            # Просто добавляем нового учителя в список
            detail_msg = _("Lehrer wurde Ihrem Konto hinzugefügt")
        else:
            # Если пользователь новый — создаем его
            user = User.objects.create_user(
                username=username,
                email=invitation.email,
                password=password
            )
            detail_msg = _("Konto erstellt und mit dem Lehrer verknüpft")

        # 2. Добавляем учителя, который прислал приглашение
        user.teachers.add(invitation.teacher)

        invitation.is_used = True
        invitation.save()

        return Response({"detail": detail_msg})