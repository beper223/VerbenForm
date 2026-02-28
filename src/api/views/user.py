from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from src.users.permissions import IsTeacher
from src.api.serializers import UserShortSerializer, UserProfileSerializer


class UserProfileViewSet(viewsets.ViewSet):
    """Управление своим профилем"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)

            # PATCH: передаем partial=True, чтобы можно было обновить только одно поле
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TeacherViewSet(viewsets.ViewSet):
    """Специальные эндпоинты для учителей"""
    permission_classes = [IsTeacher]

    @action(detail=False, methods=['get'])
    def students(self, request):
        """Список всех учеников текущего учителя"""
        students = request.user.students.all()
        # Используем сериализатор для списка учеников
        serializer = UserShortSerializer(students, many=True)
        return Response(serializer.data)