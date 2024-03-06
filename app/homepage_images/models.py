from django.db import models
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
import os

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

class Image(models.Model):
    image = models.ImageField(upload_to='homepage_images/images/')
    thumbnail = models.ImageField(upload_to='homepage_images/thumbnails/', blank=True, null=True)   
    image_url = models.TextField(blank=True)
    thumbnail_url = models.TextField(blank=True)


    def save(self, *args, **kwargs):
        if self.image:
            self.image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.image.name}"
        if self.thumbnail:
            
            self.thumbnail_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.thumbnail.name}"
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"
