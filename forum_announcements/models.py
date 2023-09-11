from django.db import models, connection
from users.models import User

class forumAnnouncements(models.Model):

    title = models.TextField(blank=True)
    content = models.TextField(blank=True,null=True)
    poster_image = models.ImageField(upload_to='forum/events/posters/',blank=True)
    poster_image_url = models.TextField(blank=True,null=True)
    thumbnail_poster_image = models.ImageField(upload_to='forum/events/thumbnails/', blank=True, null=True) 
    thumbnail_poster_image_url = models.TextField(blank=True,null=True) 
    whatsapp_link = models.TextField(blank=True,null=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    published_by = models.CharField(max_length=100,blank=True)
    hashtags = models.TextField(blank=True,null=True)
    
    def save(self, *args, **kwargs):
        if self.poster_image:
            self.poster_image_url = f"forum/events/cec/api/events/{self.id}/file/"
        if self.thumbnail_poster_image:
            self.thumbnail_poster_image_url = f"forum/events/cec/api/events/{self.id}/thumbnail/"

        super().save(*args, **kwargs)
    
class LikeAnnouncement(models.Model):
    event_id = models.ForeignKey(forumAnnouncements, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,blank=True,null=True)
    name = models.TextField()
    date = models.DateTimeField(auto_now_add=True)