from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from src.users.models import User, StudentInvitation
from src.users.services import InvitationService
from src.users.permissions import IsTeacher


class AuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[IsTeacher])
    def invite_student(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        invitation = InvitationService.create_invitation(request.user, email)
        return Response({
            "detail": "Invitation sent",
            "code": invitation.code
        })

    @action(detail=False, methods=['post'], permission_classes=[])  # AllowAny
    def activate_student(self, request):
        code = request.data.get("code")
        username = request.data.get("username")
        password = request.data.get("password")

        invitation = get_object_or_404(StudentInvitation, code=code, is_used=False)

        # 1.  Создаем ученика
        user = User.objects.create_user(
            username=username,
            email=invitation.email,
            password=password,
        )
        # 2. Добавляем учителя, который прислал приглашение
        user.teachers.add(invitation.teacher)

        invitation.is_used = True
        invitation.save()

        return Response({"detail": "User created successfully"})