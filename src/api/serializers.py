from rest_framework import serializers
from src.personal_forms.models import LearningUnit, UserVerbProgress, Verb
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class VerbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verb
        fields = ["id", "infinitive", "verb_type", "is_trennbare", "reflexivitaet"]


class LearningUnitSerializer(serializers.ModelSerializer):
    verbs = VerbSerializer(many=True, read_only=True)

    class Meta:
        model = LearningUnit
        fields = ["id", "title", "level", "skill_type", "order", "verbs"]


class UserVerbProgressSerializer(serializers.ModelSerializer):
    verb = VerbSerializer(read_only=True)

    class Meta:
        model = UserVerbProgress
        fields = [
            "id",
            "verb",
            "skill_type",
            "pronoun",
            "correct_count",
            "wrong_count",
            "streak",
            "mastered",
            "last_answer_at",
        ]

class UserShortSerializer(serializers.ModelSerializer):
    """Для отображения базовой инфо о пользователе (например, список учеников)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    """Для эндпоинта /me/ (просмотр и редактирование)"""
    is_teacher = serializers.SerializerMethodField()
    # ChoiceField сам провалидирует язык по списку из settings
    language = serializers.ChoiceField(choices=settings.LANGUAGES)

    class Meta:
        model = User
        fields = ['username', 'email', 'language', 'is_teacher']
        read_only_fields = ['username', 'is_teacher']

    def get_is_teacher(self, obj):
        return obj.groups.filter(name__in=['Teachers', 'SuperTeachers']).exists()

class RegisterSerializer(serializers.ModelSerializer):
    """Для самостоятельной регистрации"""
    password = serializers.CharField(write_only=True)
    language = serializers.ChoiceField(choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'language']

    def create(self, validated_data):
        # Используем create_user, чтобы пароль захешировался
        return User.objects.create_user(**validated_data)

class StudentActivationSerializer(serializers.Serializer):
    """Для активации по коду"""
    code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)