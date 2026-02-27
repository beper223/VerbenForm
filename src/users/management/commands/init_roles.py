from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from src.personal_forms.models import Verb

class Command(BaseCommand):
    help = 'Инициализация групп Teachers и SuperTeachers'

    def handle(self, *args, **options):
        t_group, _ = Group.objects.get_or_create(name='Teachers')
        st_group, _ = Group.objects.get_or_create(name='SuperTeachers')

        # Даем SuperTeachers права на редактирование глаголов
        verb_ct = ContentType.objects.get_for_model(Verb)
        permissions = Permission.objects.filter(content_type=verb_ct)
        for perm in permissions:
            st_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('Successfully initialized Teachers and SuperTeachers groups'))