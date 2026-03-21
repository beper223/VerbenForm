import random
from typing import Optional, List, Tuple
from django.core.cache import cache
from src.common.choices import SkillType, Pronoun
from src.personal_forms.domain import LearningAtom
from src.personal_forms.models import UserVerbProgress


class CachedTrainingEngine:
    CACHE_TTL = 90
    HISTORY_KEY_PREFIX = "training_history"
    HISTORY_SIZE = 5

    WEIGHTS = {
        'new': 60,
        'learning': 35,
        'mastered': 5
    }

    def get_next_atom(self, *, user, learning_unit) -> Optional[LearningAtom]:
        skill_type = learning_unit.skill_type
        verb_ids = list(learning_unit.verbs.values_list("id", flat=True))
        if not verb_ids:
            return None

        progress_map = self._get_cached_progress(
            user_id=user.id, unit_id=learning_unit.id,
            verb_ids=verb_ids, skill_type=skill_type
        )
        history = self._get_history(user.id, learning_unit.id)

        # Список кортежей (verb_id, pronoun)
        all_options = self._generate_options(verb_ids, skill_type)

        # 1. Первая попытка: С фильтром истории (чтобы не повторяться)
        atom = self._pick_atom(all_options, progress_map, skill_type, history_to_exclude=history)

        # 2. Вторая попытка (Fallback): Если история заблокировала всё, пробуем без неё
        if not atom:
            atom = self._pick_atom(all_options, progress_map, skill_type, history_to_exclude=[])

        if atom:
            self._update_history(user.id, learning_unit.id, atom.verb_id)

        return atom

    def _pick_atom(self, options, progress_map, skill_type, history_to_exclude) -> Optional[LearningAtom]:
        """
        Основная логика выбора. Теперь использует progress_map даже в fallback-режиме.
        """
        buckets = {'new': [], 'learning': [], 'mastered': []}

        for verb_id, pronoun in options:
            # Пропускаем, если в истории, НО только если в юните достаточно слов для маневра
            if verb_id in history_to_exclude and len(options) > self.HISTORY_SIZE:
                continue

            p_data = progress_map.get((verb_id, pronoun))

            if p_data is None:
                buckets['new'].append((verb_id, pronoun))
            elif p_data['mastered']:
                buckets['mastered'].append((verb_id, pronoun))
            else:
                # Взвешивание внутри бакета Learning (Mistake-Driven)
                # Если p_data это dict из _get_cached_progress:
                weight = 1 + p_data.get('wrong_count', 0) - p_data.get('streak', 0)
                buckets['learning'].append(((verb_id, pronoun), max(1, weight)))

        # Выбираем имя бакета (new, learning или mastered)
        chosen_bucket_name = self._weighted_bucket_choice(buckets)
        if not chosen_bucket_name:
            return None

        # Выбор конкретного глагола/местоимения
        if chosen_bucket_name == 'learning':
            candidates = [item[0] for item in buckets['learning']]
            weights = [item[1] for item in buckets['learning']]
            verb_id, pronoun = random.choices(candidates, weights=weights, k=1)[0]
        else:
            verb_id, pronoun = random.choice(buckets[chosen_bucket_name])

        # Создаем LearningAtom со всеми обязательными полями
        return LearningAtom(
            verb_id=verb_id,
            skill_type=skill_type,
            pronoun=pronoun
        )

    # Вспомогательные методы
    def _weighted_bucket_choice(self, buckets) -> Optional[str]:
        active_weights = {n: self.WEIGHTS[n] for n in buckets if buckets[n]}
        if not active_weights: return None
        return random.choices(list(active_weights.keys()), weights=list(active_weights.values()), k=1)[0]

    @staticmethod
    def _generate_options(verb_ids, skill_type) -> List[Tuple]:
        if skill_type == SkillType.TRANSLATION:
            return [(v_id, None) for v_id in verb_ids]
        return [(v_id, p.value) for v_id in verb_ids for p in Pronoun]

    def _get_history(self, user_id, unit_id):
        return cache.get(f"{self.HISTORY_KEY_PREFIX}:{user_id}:{unit_id}", [])

    def _update_history(self, user_id, unit_id, verb_id):
        key = f"{self.HISTORY_KEY_PREFIX}:{user_id}:{unit_id}"
        h = self._get_history(user_id, unit_id)
        h = (h + [verb_id])[-self.HISTORY_SIZE:]  # Держим срез последних N
        cache.set(key, h, self.CACHE_TTL)

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

        # Добавляем streak и wrong_count для тонкой настройки весов внутри бакетов
        progresses = UserVerbProgress.objects.filter(
            user_id=user_id,
            skill_type=skill_type,
            verb_id__in=verb_ids,
        ).values("verb_id", "pronoun", "mastered", "streak", "wrong_count")

        progress_map = {}
        for p in progresses:
            key = (p["verb_id"], p["pronoun"])
            # Храним данные в виде словаря для гибкости
            progress_map[key] = {
                "mastered": p["mastered"],
                "streak": p["streak"],
                "wrong_count": p["wrong_count"]
            }

        cache.set(cache_key, progress_map, self.CACHE_TTL)
        return progress_map