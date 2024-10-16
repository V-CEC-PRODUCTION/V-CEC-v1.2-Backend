from django.db import models
from azure.storage.blob import BlobServiceClient
import os

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

class User(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=130)
    role = models.CharField(max_length=50, default="student")
    name = models.CharField(max_length=100,default='')
    branch = models.TextField(blank=True, null=True)
    semester = models.TextField(max_length=10, blank=True, null=True)
    division = models.CharField(max_length=1, blank=True, null=True)
    admission_no = models.CharField(max_length=20,blank=True, null=True)
    register_no = models.CharField(max_length=20,blank=True, null=True)
    ieee_membership_no = models.CharField(max_length=10,blank=True, null=True, default='')
    gender = models.CharField(max_length=10,blank=True, null=True)
    login_type = models.CharField(max_length=50, default="email")
    profile_image = models.ImageField(upload_to='users/images/', blank=True, null=True)
    thumbnail_profile_image = models.ImageField(upload_to='users/thumbnails/', blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    thumbnail_url = models.TextField(blank=True, null=True)
    device_id = models.TextField(blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        if self.profile_image:
            self.image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.profile_image.name}"
        if self.thumbnail_profile_image:
            self.thumbnail_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.thumbnail_profile_image.name}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"User {self.id}"
    
    
class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.id}"
    
    


