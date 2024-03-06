from django.db import models
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
import os

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

class FileStore(models.Model):
    media_file = models.FileField(upload_to='gallery/cec/images/')
    thumbnail = models.ImageField(upload_to='gallery/cec/thumbnails/', blank=True, null=True)   
    media_url = models.TextField(blank=True)
    thumbnail_url = models.TextField(blank=True)
    tag=models.TextField(default="img")
    upload_time = models.DateTimeField(auto_now_add=True)
    video_url=models.TextField(blank=True)


    def save(self, *args, **kwargs):
        if self.media_file:
            self.media_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.media_file.name}"
        if self.thumbnail:
            self.thumbnail_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.thumbnail.name}"
        

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"
    
    
    
class VideoStore(models.Model):
    video_file = models.FileField(upload_to='gallery/cec/videos/')
    fid = models.ForeignKey(FileStore, on_delete=models.CASCADE, blank=False, null=False)
    video_url = models.TextField(blank=True)
    

    def save(self, *args, **kwargs):
        if self.video_file:
            self.video_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.video_file.name}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Video {self.id}"