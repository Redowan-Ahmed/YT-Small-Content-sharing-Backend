# Generated by Django 5.1.2 on 2024-11-02 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0013_alter_content_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='duration',
            field=models.CharField(blank=True, default=0, max_length=200),
        ),
        migrations.AlterField(
            model_name='content',
            name='status',
            field=models.CharField(choices=[('Draft', 'Draft'), ('Published', 'Published'), ('Archived', 'Archived'), ('Processing', 'Processing'), ('Process Completed', 'Process Completed'), ('Hide', 'Hide')], db_index=True, default='Draft', max_length=100),
        ),
    ]
