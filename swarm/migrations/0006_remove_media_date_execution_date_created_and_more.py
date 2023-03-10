# Generated by Django 4.0.3 on 2022-03-24 02:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0005_rename_run_execution_rename_reporter_media_execution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='date',
        ),
        migrations.AddField(
            model_name='execution',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='media',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='media',
            name='date_media',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
