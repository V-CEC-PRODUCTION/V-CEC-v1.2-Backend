# Generated by Django 4.1.13 on 2023-11-05 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_update_board', '0003_teamitems'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamScoreAudit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(max_length=10)),
                ('team_id', models.TextField()),
                ('score', models.TextField()),
            ],
        ),
    ]
