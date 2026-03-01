from rest_framework import serializers
from src.personal_forms.models import LearningUnit, UserVerbProgress, Verb


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