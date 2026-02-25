from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
import random

from src.personal_forms.models import LearningUnit, UserVerbProgress
from src.personal_forms.services import CachedTrainingEngine, DistractorGenerator, ProgressService
from src.common.choices import SkillType, Pronoun, Tense

class TrainingViewSet(viewsets.ViewSet):
    """
    API для получения карточек обучения и регистрации ответов.
    """
    permission_classes = [permissions.IsAuthenticated]
    CACHE_TTL = 60

    @action(detail=False, methods=["get"])
    def next_card(self, request):
        unit_id = request.query_params.get("learning_unit_id")
        if not unit_id:
            return Response({"detail": "learning_unit_id required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            unit = LearningUnit.objects.get(id=unit_id)
        except LearningUnit.DoesNotExist:
            return Response({"detail": "LearningUnit not found"}, status=status.HTTP_404_NOT_FOUND)

        engine = CachedTrainingEngine()
        atom = engine.get_next_atom(user=request.user, learning_unit=unit)

        if not atom:
            return Response({"detail": "No more cards available"}, status=status.HTTP_200_OK)

        # Определяем правильный ответ
        if atom.skill_type == SkillType.TRANSLATION:
            correct_answer = getattr(atom.verb, request.query_params.get("language", "translation_en"))
            distractors = DistractorGenerator().translation_distractors(
                verb=atom.verb,
                learning_unit=unit,
                language=request.query_params.get("language", "en"),
            )
        else:
            # skill_type = conjugation
            tense = Tense.PRAESENS if atom.skill_type == SkillType.PRAESENS else Tense.PRAETERITUM
            correct_answer = CachedTrainingEngine().get_conjugation(atom)
            distractors = DistractorGenerator().conjugation_distractors(
                verb=atom.verb,
                tense=tense,
                pronoun=atom.pronoun,
                correct_answer=correct_answer
            )

        # Формируем варианты ответа
        choices = distractors[:3] + [correct_answer]
        random.shuffle(choices)

        # Сохраняем карточку в Redis
        cache_key = f"current_card:{request.user.id}"
        cache.set(cache_key, {
            "unit_id": unit.id,
            "verb_id": atom.verb.id,
            "skill_type": atom.skill_type,
            "pronoun": atom.pronoun,
            "correct_answer": correct_answer,
        }, timeout=self.CACHE_TTL)

        return Response({
            "card_id": cache_key,
            "verb": atom.verb.infinitive,
            "skill_type": atom.skill_type,
            "pronoun": atom.pronoun,
            "choices": choices,
        })

    @action(detail=False, methods=["post"])
    def answer(self, request):
        card_id = request.data.get("card_id")
        user_answer = request.data.get("answer")
        if not card_id or user_answer is None:
            return Response({"detail": "card_id and answer required"}, status=status.HTTP_400_BAD_REQUEST)

        card_data = cache.get(card_id)
        if not card_data:
            return Response({"detail": "Card expired or not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем прогресс
        from src.personal_forms.models import Verb
        verb = Verb.objects.get(id=card_data["verb_id"])
        progress = ProgressService.get_or_create_progress(
            user=request.user,
            verb=verb,
            skill_type=card_data["skill_type"],
            pronoun=card_data["pronoun"]
        )

        # Проверяем ответ
        correct_answer = card_data["correct_answer"]
        is_correct = str(user_answer).strip() == str(correct_answer).strip()

        # Обновляем прогресс
        ProgressService().record_answer(progress=progress, is_correct=is_correct)

        # Удаляем карточку из кеша
        cache.delete(card_id)

        return Response({
            "correct": is_correct,
            "correct_answer": correct_answer,
            "mastered": progress.mastered,
            "streak": progress.streak,
        })