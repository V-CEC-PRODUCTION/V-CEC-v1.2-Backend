# Generated by Django 4.1.13 on 2023-11-06 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_update_board', '0007_remove_teamitems_status_teamitems_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamitems',
            name='item_id',
            field=models.IntegerField(default=0),
        ),
    ]
