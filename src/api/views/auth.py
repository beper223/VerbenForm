from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

from src.users.models import StudentInvitation

from src.api.serializers import (
    RegisterSerializer,
    StudentActivationSerializer
)

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Самостоятельная регистрация ученика (без инвайта)"""
        serializer = RegisterSerializer(data=request.data)
        # raise_exception=True автоматически вернет 400 с текстом ошибки
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Registrierung erfolgreich")}, status=201)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Обычная авторизация"""
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "language": user.language  # Возвращаем язык из БД!
            })

        return Response({"error": _("Falsche Anmeldedaten")}, status=401)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Удаление токена (выход из системы)"""
        # Просто удаляем токен текущего пользователя в базе
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": _("Erfolgreich abgemeldet")}, status=200)

    @action(detail=False, methods=['post'], permission_classes=[])  # AllowAny
    def activate_student(self, request):
        """Эндпоинт для ученика: первый вход по коду"""
        serializer = StudentActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        invitation = get_object_or_404(StudentInvitation, code=data['code'], is_used=False)

        # 1. Проверяем, существует ли уже такой пользователь
        user = User.objects.filter(email=invitation.email).first()

        detail_msg = _("Lehrer wurde Ihrem Konto hinzugefügt")
        if not user:
            user = User.objects.create_user(
                username=data['username'],
                email=invitation.email,
                password=data['password']
            )
            detail_msg = _("Konto erstellt und mit dem Lehrer verknüpft")

        # 2. Добавляем учителя, который прислал приглашение
        user.teachers.add(invitation.teacher)

        invitation.is_used = True
        invitation.save()

        return Response({"detail": detail_msg})