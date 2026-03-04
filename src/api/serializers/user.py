from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    """Для отображения базовой инфо о пользователе (например, список учеников)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    """Для эндпоинта /me/ (просмотр и редактирование)"""
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.STUDENT)
    # ChoiceField сам провалидирует язык по списку из settings
    language = serializers.ChoiceField(choices=settings.LANGUAGES)
    # birth_date = serializers.DateField(
    #     required=False,
    #     allow_null=True
    # )
    class Meta:
        model = User
        fields = ['username', 'email', 'language', 'role', 'birth_date']
        read_only_fields = ['username', 'role']

    # def get_is_teacher(self, obj):
    #     return obj.groups.filter(name__in=['Teachers', 'SuperTeachers']).exists()