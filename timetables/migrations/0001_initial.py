# Generated by Django 4.2.4 on 2023-09-11 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimeTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstcode', models.TextField()),
                ('secondcode', models.TextField()),
                ('thirdcode', models.TextField()),
                ('fourthcode', models.TextField()),
                ('fifthcode', models.TextField()),
                ('sixthcode', models.TextField()),
                ('firsttime', models.TextField(default='09-10')),
                ('secondtime', models.TextField(default='10-11')),
                ('thirdtime', models.TextField(default='11-12')),
                ('fourthtime', models.TextField(default='01-02')),
                ('fifthtime', models.TextField(default='02-03')),
                ('sixthtime', models.TextField(default='03-04')),
                ('currentcode', models.TextField(default='0')),
                ('currenttime', models.TextField(default='0')),
                ('day', models.IntegerField(default=0)),
                ('semester', models.CharField(max_length=3)),
                ('division', models.CharField(max_length=2)),
            ],
        ),
    ]
