# Generated by Django 5.1.2 on 2024-10-19 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, db_index=True, max_length=16),
        ),
    ]
