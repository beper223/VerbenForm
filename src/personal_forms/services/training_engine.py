import random
from typing import Optional

from django.core.cache import cache

from src.personal_forms.models import UserVerbProgress
from src.common.choices import SkillType, Pronoun
from src.personal_forms.domain import LearningAtom


class CachedTrainingEngine:

    CACHE_TTL = 90  # seconds

    NEW_WEIGHT = 0.6
    LEARNING_WEIGHT = 0.35
    MASTERED_WEIGHT = 0.05

    def get_next_atom(self, *, user, learning_unit) -> Optional[LearningAtom]:

        skill_type = learning_unit.skill_type
        verb_ids = list(
            learning_unit.verbs.values_list("id", flat=True)
        )

        if not verb_ids:
            return None

        # 1️⃣ Получаем progress_map из кеша
        progress_map = self._get_cached_progress(
            user_id=user.id,
            unit_id=learning_unit.id,
            verb_ids=verb_ids,
            skill_type=skill_type,
        )

        # 2️⃣ Делим на bucket'ы
        new_candidates = []
        learning_candidates = []
        mastered_candidates = []

        if skill_type == SkillType.TRANSLATION:

            for verb_id in verb_ids:
                key = (verb_id, None)
                progress = progress_map.get(key)

                if progress is None:
                    new_candidates.append(key)
                elif progress:
                    mastered_candidates.append(key)
                else:
                    learning_candidates.append(key)

        else:
            for verb_id in verb_ids:
                for pronoun in Pronoun:
                    key = (verb_id, pronoun.value)
                    progress = progress_map.get(key)

                    if progress is None:
                        new_candidates.append(key)
                    elif progress:
                        mastered_candidates.append(key)
                    else:
                        learning_candidates.append(key)

        bucket = self._choose_bucket(
            new_candidates,
            learning_candidates,
            mastered_candidates,
        )

        if not bucket:
            return None

        verb_id, pronoun = random.choice(bucket)

        # verbs_map = {
        #     v.id: v
        #     for v in learning_unit.verbs.all()
        # }

        return LearningAtom(
            verb_id=verb_id,
            skill_type=skill_type,
            pronoun=pronoun,
        )

    # --------------------------------------------------

    def _get_cached_progress(
        self,
        *,
        user_id,
        unit_id,
        verb_ids,
        skill_type,
    ):

        cache_key = f"progress:{user_id}:{unit_id}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        progresses = UserVerbProgress.objects.filter(
            user_id=user_id,
            skill_type=skill_type,
            verb_id__in=verb_ids,
        ).values("verb_id", "pronoun", "mastered")

        progress_map = {}

        for p in progresses:
            key = (p["verb_id"], p["pronoun"])
            progress_map[key] = p["mastered"]

        cache.set(cache_key, progress_map, self.CACHE_TTL)

        return progress_map

    # --------------------------------------------------

    def _choose_bucket(
        self,
        new_candidates,
        learning_candidates,
        mastered_candidates,
    ):

        weighted_pool = []

        # 1. Если есть что учить (New или Learning)
        if new_candidates or learning_candidates:
            if new_candidates:
                weighted_pool.extend([new_candidates] * int(self.NEW_WEIGHT * 100))
            if learning_candidates:
                weighted_pool.extend([learning_candidates] * int(self.LEARNING_WEIGHT * 100))
            if mastered_candidates:
                weighted_pool.extend([mastered_candidates] * int(self.MASTERED_WEIGHT * 100))

            return random.choice(weighted_pool)

        # 2. Если ВСЕ слова в юните уже MASTERED (режим Повторения)
        if mastered_candidates:
            return mastered_candidates  # Просто выбираем любое из выученных

        return None
