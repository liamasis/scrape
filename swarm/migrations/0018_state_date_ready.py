# Generated by Django 4.0.5 on 2022-06-23 01:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0017_alter_state_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='date_ready',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
