# Generated by Django 4.0.3 on 2022-03-24 02:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swarm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('media_id', models.CharField(max_length=255)),
                ('media_pk', models.CharField(max_length=255)),
                ('media_type', models.IntegerField(choices=[(0, 'UNKNOWN'), (1, 'Photo'), (2, 'Video'), (8, 'Album')], default=0)),
                ('caption_text', models.TextField()),
                ('comment_count', models.IntegerField(default=0)),
                ('like_count', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(0, 'Processing'), (1, 'Ready'), (2, 'Shown')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('completed', models.BooleanField(default=False)),
                ('shown', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='Todo',
        ),
        migrations.AddField(
            model_name='media',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='swarm.run'),
        ),
    ]