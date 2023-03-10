# Generated by Django 4.0.3 on 2022-03-24 03:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0009_session_alter_instagramaccount_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='handle',
            new_name='title',
        ),
        migrations.AddField(
            model_name='instagramaccount',
            name='session',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='swarm.session'),
            preserve_default=False,
        ),
    ]
