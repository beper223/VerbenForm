from typing import Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q

from src.personal_forms.models import UserVerbProgress, LearningUnit
from src.common.choices import SkillType, Pronoun, LearningStatus
from src.personal_forms.domain import LearningAtom

User = get_user_model()


class LearningUnitProgressService:

    @staticmethod
    def generate_atoms(learning_unit: LearningUnit) -> List[LearningAtom]:
        """
        Генерирует все атомы обучения внутри LearningUnit.
        """

        verbs = learning_unit.verbs.all()
        skill_type = learning_unit.skill_type

        if skill_type == SkillType.TRANSLATION:
            pronouns: List[Optional[str]] = [None]
        else:
            pronouns = [p.value for p in Pronoun]

        atoms: List[LearningAtom] = []

        for verb in verbs:
            for pronoun in pronouns:
                atoms.append(
                    LearningAtom(
                        verb_id=verb.id,
                        skill_type=skill_type,
                        pronoun=pronoun,
                    )
                )

        return atoms

    def build_progress(
        self,
        *,
        user: User,
        learning_unit: LearningUnit,
    ) -> Dict:
        atoms = self.generate_atoms(learning_unit)

        verb_ids = {atom.verb_id for atom in atoms}

        progresses = UserVerbProgress.objects.filter(
            user=user,
            verb_id__in=verb_ids,
            skill_type=learning_unit.skill_type,
        )

        progress_map: Dict[Tuple[int, Optional[str]], UserVerbProgress] = {
            (p.verb_id, p.pronoun): p
            for p in progresses
        }

        verbs_map = {v.id: v for v in learning_unit.verbs.all()}

        matrix: Dict[str, Dict[str, LearningStatus]] = {}
        mastered_atoms = 0

        for atom in atoms:
            key = (atom.verb_id, atom.pronoun)
            progress = progress_map.get(key)

            if progress is None:
                status = LearningStatus.NEW
            elif progress.mastered:
                status = LearningStatus.MASTERED
                mastered_atoms += 1
            else:
                status = LearningStatus.LEARNING

            verb = verbs_map.get(atom.verb_id)
            verb_key = verb.infinitive if verb else f"verb:{atom.verb_id}"
            pronoun_key = atom.pronoun or "-"

            if verb_key not in matrix:
                matrix[verb_key] = {}

            matrix[verb_key][pronoun_key] = status

        total_atoms = len(atoms)
        percent = int((mastered_atoms / total_atoms) * 100) if total_atoms else 0
        completed = mastered_atoms == total_atoms and total_atoms > 0

        return {
            "matrix": matrix,
            "total_atoms": total_atoms,
            "mastered_atoms": mastered_atoms,
            "percent": percent,
            "completed": completed,
        }

    def get_global_stats(self, user: User) -> Dict:
        """
        Общая статистика пользователя по всем глаголам и навыкам.
        """
        stats = UserVerbProgress.objects.filter(user=user).aggregate(
            total_mastered=Count('id', filter=Q(mastered=True)),
            total_correct=Sum('correct_count', default=0),
            total_wrong=Sum('wrong_count', default=0),
        )

        total_ans = stats['total_correct'] + stats['total_wrong']
        accuracy = round((stats['total_correct'] / total_ans) * 100, 1) if total_ans > 0 else 0

        return {
            "total_mastered": stats['total_mastered'],
            "total_correct": stats['total_correct'],
            "total_wrong": stats['total_wrong'],
            "accuracy": accuracy
        }

    def get_units_overview(self, user: User, units: List[LearningUnit]) -> List[Dict]:
        """
        Эффективный расчет прогресса для списка уроков (без N+1 запросов).
        """
        # 1. Получаем ВЕСЬ прогресс пользователя одним запросом
        all_user_progress = UserVerbProgress.objects.filter(user=user).values(
            'verb_id', 'skill_type', 'pronoun', 'mastered'
        )

        # 2. Группируем прогресс по типу навыка для быстрого поиска
        # Ключ: (verb_id, skill_type, pronoun)
        progress_lookup = {
            (p['verb_id'], p['skill_type'], p['pronoun']): p['mastered']
            for p in all_user_progress
        }

        overview = []
        for unit in units:
            # Для каждого юнита генерируем его "атомы"
            atoms = self.generate_atoms(unit)
            total_atoms = len(atoms)

            # Считаем, сколько из них mastered, используя наш lookup (без запросов к БД!)
            mastered_count = 0
            for atom in atoms:
                is_mastered = progress_lookup.get((atom.verb_id, atom.skill_type, atom.pronoun), False)
                if is_mastered:
                    mastered_count += 1

            percent = int((mastered_count / total_atoms) * 100) if total_atoms else 0

            overview.append({
                "id": unit.id,
                "title": unit.title,
                "level": unit.level,
                "skill_type": unit.skill_type,
                "percent": percent,
                "mastered_atoms": mastered_count,
                "total_atoms": total_atoms,
                "completed": mastered_count == total_atoms and total_atoms > 0
            })

        return overview