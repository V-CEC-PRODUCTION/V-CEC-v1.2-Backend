# Generated by Django 4.1.13 on 2024-03-13 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cecify', '0004_radioepisodesdetails_season_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='radioepisodesdetails',
            name='episode',
            field=models.IntegerField(),
        ),
    ]
