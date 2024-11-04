# Generated by Django 5.1.2 on 2024-10-26 19:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='video',
        ),
        migrations.AddField(
            model_name='videofile',
            name='content',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='channel.content'),
        ),
    ]
