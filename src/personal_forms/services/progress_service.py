from django.db import transaction
from django.utils import timezone

from src.personal_forms.models import UserVerbProgress


class ProgressService:
    """
    Отвечает ТОЛЬКО за обновление прогресса.
    Не знает ничего про карточки, модули и UI.
    """

    STREAK_TO_MASTER = 5

    # --------------------------------------------------

    @staticmethod
    def get_or_create_progress(
        *,
        user,
        verb,
        skill_type,
        pronoun=None,
    ) -> UserVerbProgress:

        progress, _ = UserVerbProgress.objects.get_or_create(
            user=user,
            verb=verb,
            skill_type=skill_type,
            pronoun=pronoun,
        )
        return progress

    # --------------------------------------------------

    @transaction.atomic
    def record_answer(
        self,
        *,
        progress: UserVerbProgress,
        is_correct: bool,
    ) -> None:

        if is_correct:
            self._handle_correct(progress)
        else:
            self._handle_wrong(progress)

        progress.last_answer_at = timezone.now()

        progress.save(update_fields=[
            "correct_count",
            "wrong_count",
            "streak",
            "mastered",
            "last_answer_at",
            "updated_at",
        ])

    # --------------------------------------------------

    def _handle_correct(self, progress: UserVerbProgress) -> None:

        progress.correct_count += 1
        progress.streak += 1

        if (
            not progress.mastered
            and progress.streak >= self.STREAK_TO_MASTER
        ):
            progress.mastered = True

    # --------------------------------------------------

    @staticmethod
    def _handle_wrong(progress: UserVerbProgress) -> None:

        progress.wrong_count += 1
        progress.streak = 0

        # 🔥 Не снимаем mastered автоматически