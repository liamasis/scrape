# Generated by Django 4.0.6 on 2022-08-01 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0031_instagramloginaccount_last_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramloginaccount',
            name='error_count',
            field=models.IntegerField(default=0),
        ),
    ]
