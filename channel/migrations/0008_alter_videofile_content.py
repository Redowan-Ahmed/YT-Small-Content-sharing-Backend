# Generated by Django 5.1.2 on 2024-10-30 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0007_alter_videofile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videofile',
            name='content',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='channel.content'),
        ),
    ]
