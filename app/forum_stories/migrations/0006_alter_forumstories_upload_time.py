# Generated by Django 4.2.4 on 2023-09-17 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_stories', '0005_alter_forumstories_upload_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumstories',
            name='upload_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
