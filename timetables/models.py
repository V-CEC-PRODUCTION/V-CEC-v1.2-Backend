from django.db import models

# Create your models here.
class TimeTable(models.Model):
    firstcode=models.TextField()
    secondcode=models.TextField()
    thirdcode=models.TextField()
    fourthcode=models.TextField()
    fifthcode=models.TextField()
    sixthcode=models.TextField()
    firsttime=models.TextField(default='09:00-10:00')
    secondtime=models.TextField(default='10:00-11:00')
    thirdtime=models.TextField(default='11:00-12:00')
    fourthtime=models.TextField(default='01:00-02:00')
    fifthtime=models.TextField(default='02:00-03:00')
    sixthtime=models.TextField(default='03:00-04:00')
    currentcode=models.TextField(default='0')
    currenttime=models.TextField(default='0')
    day=models.IntegerField(default=0)
    semester=models.CharField(max_length=3)
    division=models.CharField(max_length=2)