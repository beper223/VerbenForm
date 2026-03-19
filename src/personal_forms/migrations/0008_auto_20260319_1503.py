from django.db import migrations


def link_groups_to_authors(apps, schema_editor):
    VerbGroup = apps.get_model('personal_forms', 'VerbGroup')

    for group in VerbGroup.objects.all():
        if group.course:
            # Копируем автора из курса в группу
            group.author = group.course.author
            group.save()


class Migration(migrations.Migration):
    dependencies = [
        ('personal_forms', '0007_verbgroup_author_alter_learningunit_verb_group_and_more'),
    ]
    operations = [
        migrations.RunPython(link_groups_to_authors),
    ]
