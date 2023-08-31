from django.db import models

class FileStore(models.Model):
    media_file = models.FileField(upload_to='gallery/cec/images/')
    thumbnail = models.ImageField(upload_to='gallery/cec/thumbnails/', blank=True, null=True)   
    media_url = models.TextField(blank=True)
    thumbnail_url = models.TextField(blank=True)
    tag=models.TextField(default="img")
    upload_time = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.media_file:
            self.media_url = f"gallery/cec/api/media/{self.id}/file/"
        if self.thumbnail:
            self.thumbnail_url = f"gallery/cec/api/media/{self.id}/thumbnail/"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"
    
    
    
class VideoStore(models.Model):
    video_file = models.FileField(upload_to='gallery/cec/videos/')
    fid = models.ForeignKey(FileStore, on_delete=models.CASCADE, blank=False, null=False)
    video_url = models.TextField(blank=True)
    

    def save(self, *args, **kwargs):
        if self.video_file:
            self.video_url = f"gallery/cec/api/media/files/video/{self.id}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Video {self.id}"