# Generated by Django 4.2.4 on 2023-08-31 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='login_type',
            field=models.CharField(default='email', max_length=50),
        ),
    ]
