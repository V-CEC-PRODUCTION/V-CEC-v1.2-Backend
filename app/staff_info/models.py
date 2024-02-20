from django.db import models


class staffInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=False)
    designation = models.TextField()
    email_id = models.TextField()
    mobile_no = models.TextField(unique=True)
    department = models.TextField()

