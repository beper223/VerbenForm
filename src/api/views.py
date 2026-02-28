from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from dataclasses import asdict
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

from src.users.models import StudentInvitation
from src.users.services import InvitationService
from src.users.permissions import IsTeacher

from src.personal_forms.models import LearningUnit, UserVerbProgress
from src.api.serializers import (
    LearningUnitSerializer,
    UserVerbProgressSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserShortSerializer,
    StudentActivationSerializer
)

from src.personal_forms.services import TrainingService, LearningUnitProgressService

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

class TrainingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализируем сервис один раз
        self.training_service = TrainingService()

    @action(detail=False, methods=["get"], url_path="next-card")
    def next_card(self, request):
        unit_id = request.query_params.get("learning_unit_id")
        language = request.user.language

        if not unit_id:
            return Response({"detail": _("learning_unit_id erforderlich")}, status=status.HTTP_400_BAD_REQUEST)

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