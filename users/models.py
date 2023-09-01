from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=130)
    role = models.CharField(max_length=50, default="student")
    logged_in = models.BooleanField(default=False)
    login_type = models.CharField(max_length=50, default="email")
    
    
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)

    # Add a related_name for groups and user_permissions

    groups = models.ManyToManyField(Group, blank=True, related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_permissions"
    )
    
    def __str__(self):
        return str(self.id) 

