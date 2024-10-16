# Generated by Django 4.1.13 on 2023-11-05 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_update_board', '0002_remove_teamscore_team_score_json_teamscore_score_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.TextField(default='')),
                ('item', models.TextField(default='')),
                ('points', models.IntegerField(default=0)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
