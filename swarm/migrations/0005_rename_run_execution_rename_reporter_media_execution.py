# Generated by Django 4.0.3 on 2022-03-24 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0004_alter_media_media_type_alter_run_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Run',
            new_name='Execution',
        ),
        migrations.RenameField(
            model_name='media',
            old_name='reporter',
            new_name='execution',
        ),
    ]