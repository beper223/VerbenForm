import random
from typing import List

from django.contrib.auth import get_user_model

from src.common.choices import LearningStatus
from src.personal_forms.models import LearningUnit, LearningAtom
from src.personal_forms.services import LearningUnitProgressService


User = get_user_model()


class TrainingEngine:

    def __init__(self):
        self.progress_service = LearningUnitProgressService()

    def get_next_atom(self, *, user: User, learning_unit: LearningUnit) -> LearningAtom:
        atoms = self.progress_service.generate_atoms(learning_unit)
        progress_data = self.progress_service.build_progress(
            user=user,
            learning_unit=learning_unit,
        )

        matrix = progress_data["matrix"]

        new_atoms: List[LearningAtom] = []
        learning_atoms: List[LearningAtom] = []
        mastered_atoms: List[LearningAtom] = []

        for atom in atoms:
            verb_key = atom.verb.infinitive
            pronoun_key = atom.pronoun or "-"

            status = matrix[verb_key][pronoun_key]

            if status == LearningStatus.NEW:
                new_atoms.append(atom)
            elif status == LearningStatus.LEARNING:
                learning_atoms.append(atom)
            else:
                mastered_atoms.append(atom)

        return self._choose_atom(
            new_atoms=new_atoms,
            learning_atoms=learning_atoms,
            mastered_atoms=mastered_atoms,
        )

    def _choose_atom(
        self,
        *,
        new_atoms: List[LearningAtom],
        learning_atoms: List[LearningAtom],
        mastered_atoms: List[LearningAtom],
    ) -> LearningAtom:

        # Если есть learning — приоритет
        roll = random.random()

        if learning_atoms and roll < 0.6:
            return random.choice(learning_atoms)

        if new_atoms and roll < 0.9:
            return random.choice(new_atoms)

        if mastered_atoms:
            return random.choice(mastered_atoms)

        # fallback
        pool = learning_atoms or new_atoms or mastered_atoms

        if not pool:
            raise ValueError("No atoms available in learning unit.")

        return random.choice(pool)