# Generated by Django 4.1.13 on 2023-12-09 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_events', '0013_forumevents_poster_image_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumevents',
            name='event_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
