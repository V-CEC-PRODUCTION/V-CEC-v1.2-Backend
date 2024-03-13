from django.db import models
from azure.storage.blob import BlobServiceClient
import os

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

class AddForum(models.Model):
    forum_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, default='No display name')#
    forum_description = models.TextField(default='No description')
    email_id = models.TextField()
    forum_role_name = models.CharField(max_length=100)#
    forum_image = models.ImageField(upload_to='forum/management/images/')
    thumbnail_forum_image = models.ImageField(upload_to='forum/management/thumbnails/', blank=True, null=True)
    logged_in = models.BooleanField(default=False)
    image_url = models.TextField(blank=True, null=True)#
    thumbnail_url = models.TextField(blank=True, null=True)#

        
    def save(self, *args, **kwargs):
        

        if self.forum_image:
            self.image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.forum_image.name}"
        if self.thumbnail_forum_image:
            self.thumbnail_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.thumbnail_forum_image.name}"

        super(AddForum, self).save(*args, **kwargs)

    def __str__(self):
        return f"Forum: {self.forum_name}"
    
    
class Token(models.Model):
    user = models.ForeignKey(AddForum, on_delete=models.CASCADE)
    access_token = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.id}"