# Generated by Django 4.2.4 on 2023-09-10 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_events', '0005_forumevents_poster_image_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumevents',
            name='poster_image_url',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='forumevents',
            name='thumbnail_poster_image_url',
            field=models.TextField(blank=True, null=True),
        ),
    ]
