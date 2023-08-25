from django.db import models


class staffInfo(models.Model):
    name = models.TextField(blank=False)
    designation = models.TextField()
    email_id = models.TextField()
    mobile_no = models.TextField()
    department = models.TextField()

