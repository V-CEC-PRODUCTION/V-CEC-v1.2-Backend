# Generated by Django 4.2.4 on 2023-08-27 05:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('highlights_cec', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Image',
            new_name='HighlightImage',
        ),
    ]
