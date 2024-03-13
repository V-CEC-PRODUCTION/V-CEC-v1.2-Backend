from django.db import models
from azure.storage.blob import BlobServiceClient
import os

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

class RadioSeasonDetails(models.Model):
    season = models.IntegerField(unique=True, blank=False, null=False)
    color1 = models.CharField(max_length=6, blank=False, null=False)
    color2 = models.CharField(max_length=6, blank=False, null=False)
    color3 = models.CharField(max_length=6, blank=False, null=False)
    color4 = models.CharField(max_length=6, blank=False, null=False)
    
    def __str__(self):
        return f"Season {self.season}"
    
class RadioEpisodesDetails(models.Model):
    season = models.ForeignKey(RadioSeasonDetails, on_delete=models.CASCADE)
    season_number = models.IntegerField(default=0,blank=False, null=False)
    episode = models.IntegerField(blank=False, null=False)  
    content = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to='cecify/radio/episodes/images/', blank=False, null=False)
    thumbnail = models.ImageField(upload_to='cecify/radio/episodes/thumbnails/', blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    thumbnail_url = models.TextField(blank=True, null=True)
    spotify_url = models.TextField(default='',blank=False, null=False)
    youtube_url = models.TextField(default='',blank=True, null=True)
    google_podcast_url = models.TextField(default='',blank=True, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:

        unique_together = ['episode', 'season_number']
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.image.name}"
        if self.thumbnail:
            self.thumbnail_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/media/{self.thumbnail.name}"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Episode {self.episode} of Season {self.season.season}"
