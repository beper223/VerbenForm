from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth import get_user_model

from src.personal_forms.models import UserVerbProgress, Verb
from src.common.choices import SkillType


class Command(BaseCommand):
    help = "Test Redis invalidation signal"

    def handle(self, *args, **options):

        User = get_user_model()

        user, _ = User.objects.get_or_create(
            username="signal_test_user"
        )

        verb = Verb.objects.first()
        if not verb:
            self.stdout.write(self.style.ERROR("No verbs in DB"))
            return

        progress, _ = UserVerbProgress.objects.get_or_create(
            user=user,
            verb=verb,
            skill_type=SkillType.TRANSLATION,
            pronoun=None,
        )

        cache_key = f"progress:user:{user.id}:skill:{progress.skill_type}"

        cache.set(cache_key, "TEST_VALUE", 300)
        self.stdout.write(f"Cache before save: {cache.get(cache_key)}")

        # Меняем объект — должен сработать signal
        progress.correct_count += 1
        progress.save()

        self.stdout.write(f"Cache after save: {cache.get(cache_key)}")