from django.db import models

# Create your models here.
class TimeTable(models.Model):
    firstcode=models.TextField(null=True)
    secondcode=models.TextField(null=True)
    thirdcode=models.TextField(null=True)
    fourthcode=models.TextField(null=True)
    fifthcode=models.TextField(null=True)
    sixthcode=models.TextField(null=True)
    firsttime=models.TextField(default='09:00 AM-10:00 AM')
    secondtime=models.TextField(default='10:00 AM-11:00 AM')
    thirdtime=models.TextField(default='11:00 AM-12:00 PM')
    fourthtime=models.TextField(default='01:00 PM-02:00 PM')
    fifthtime=models.TextField(default='02:00 PM-03:00 PM')
    sixthtime=models.TextField(default='03:00 PM-04:00 PM')
    currentcode=models.TextField(default='0')
    currenttime=models.TextField(default='0')
    day=models.IntegerField(default=0)
    semester=models.CharField(max_length=3)
    division=models.CharField(max_length=2)