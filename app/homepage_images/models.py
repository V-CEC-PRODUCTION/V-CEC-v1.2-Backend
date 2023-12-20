from django.db import models

class Image(models.Model):
    image = models.ImageField(upload_to='homepage_images/images/')
    thumbnail = models.ImageField(upload_to='homepage_images/thumbnails/', blank=True, null=True)   
    image_url = models.TextField(blank=True)
    thumbnail_url = models.TextField(blank=True)


    def save(self, *args, **kwargs):
        if self.image:
            self.image_url = f"homepage/api/images/{self.id}/file/"
        if self.thumbnail:
            self.thumbnail_url = f"homepage/api/images/{self.id}/thumbnail/"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"
