# Generated by Django 4.2.4 on 2023-08-27 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('highlights_cec', '0002_rename_image_highlightimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='highlightimage',
            name='upload_time',
            field=models.TextField(blank=True),
        ),
    ]
