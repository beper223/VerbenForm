from typing import Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model

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