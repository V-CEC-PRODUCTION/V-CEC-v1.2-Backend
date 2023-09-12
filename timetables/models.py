from django.db import models

# Create your models here.
class TimeTable(models.Model):
    firstcode=models.TextField()
    secondcode=models.TextField()
    thirdcode=models.TextField()
    fourthcode=models.TextField()
    fifthcode=models.TextField()
    sixthcode=models.TextField()
    firsttime=models.TextField(default='09-10')
    secondtime=models.TextField(default='10-11')
    thirdtime=models.TextField(default='11-12')
    fourthtime=models.TextField(default='01-02')
    fifthtime=models.TextField(default='02-03')
    sixthtime=models.TextField(default='03-04')
    currentcode=models.TextField(default='0')
    currenttime=models.TextField(default='0')
    day=models.IntegerField(default=0)
    semester=models.CharField(max_length=3)
    division=models.CharField(max_length=2)