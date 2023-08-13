from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=130)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default="student")
    logged_in = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
