from django.db import migrations

def migrate_verbs_to_groups(apps, schema_editor):
    # Получаем модели из исторического состояния (важно для миграций)
    LearningUnit = apps.get_model('personal_forms', 'LearningUnit')
    VerbGroup = apps.get_model('personal_forms', 'VerbGroup')

    for unit in LearningUnit.objects.all():
        # 1. Создаем новую группу для этого юнита
        # Называем её так же, как юнит, чтобы учителю было понятно
        group = VerbGroup.objects.create(
            course=unit.course,
            title=f"Set: {unit.title}"
        )

        # 2. Копируем все глаголы из старого поля в новую группу
        verbs = unit.verbs.all()
        if verbs.exists():
            group.verbs.set(verbs)

        # 3. Привязываем юнит к новой группе
        unit.verb_group = group
        unit.save()

def rollback_verbs_from_groups(apps, schema_editor):
    # Логика отката (если понадобится): возвращаем глаголы из групп в юниты
    LearningUnit = apps.get_model('personal_forms', 'LearningUnit')
    for unit in LearningUnit.objects.all():
        if unit.verb_group:
            unit.verbs.set(unit.verb_group.verbs.all())
            unit.save()

class Migration(migrations.Migration):

    dependencies = [
        # Здесь Django автоматически подставит имя предыдущей миграции
        ('personal_forms', '0004_verbgroup_learningunit_verb_group'),
    ]

    operations = [
        migrations.RunPython(migrate_verbs_to_groups, rollback_verbs_from_groups),
    ]