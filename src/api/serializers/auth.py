from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

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