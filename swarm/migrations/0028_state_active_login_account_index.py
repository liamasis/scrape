# Generated by Django 4.0.6 on 2022-07-31 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0027_alter_media_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='active_login_account_index',
            field=models.IntegerField(default=0),
        ),
    ]
