from django.db import models

class User(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=130)
    role = models.CharField(max_length=50, default="student")
    logged_in = models.BooleanField(default=False)
    login_type = models.CharField(max_length=50, default="email")
    def __str__(self):
        return str(self.id)
