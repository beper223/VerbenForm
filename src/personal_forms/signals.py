from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from src.personal_forms.models import UserVerbProgress


def build_progress_cache_key(user_id: int, skill_type: str):
    return f"progress:user:{user_id}:skill:{skill_type}"


@receiver(post_save, sender=UserVerbProgress)
def invalidate_progress_cache(sender, instance, **kwargs):
    key = build_progress_cache_key(
        user_id=instance.user_id,
        skill_type=instance.skill_type,
    )
    cache.delete(key)