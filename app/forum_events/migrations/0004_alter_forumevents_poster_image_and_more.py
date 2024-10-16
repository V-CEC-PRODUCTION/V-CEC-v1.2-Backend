# Generated by Django 4.2.4 on 2023-09-10 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_events', '0003_rename_event_likeevent_event_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumevents',
            name='poster_image',
            field=models.ImageField(blank=True, upload_to='forum/events/posters/'),
        ),
        migrations.AlterField(
            model_name='forumevents',
            name='published_by',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='forumevents',
            name='status',
            field=models.CharField(blank=True, default='Upcoming', max_length=10),
        ),
        migrations.AlterField(
            model_name='forumevents',
            name='title',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='event_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_events.forumevents'),
        ),
    ]
