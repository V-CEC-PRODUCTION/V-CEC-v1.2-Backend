from django.db import models

class HighlightImage(models.Model):
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='highlights_images/images/')
    thumbnail = models.ImageField(upload_to='highlights_images/thumbnails/', blank=True, null=True)   
    image_url = models.TextField(blank=True)
    thumbnail_url = models.TextField(blank=True)
    upload_time = models.TextField(blank=True)
    tag = models.CharField(max_length=150, blank=True)
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image_url = f"highlights/cec/api/images/{self.id}/file/"
        if self.thumbnail:
            self.thumbnail_url = f"highlights/cec/api/images/{self.id}/thumbnail/"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"