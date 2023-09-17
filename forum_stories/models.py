from django.db import models
from users.models import User
from forum_management.models import AddForum
from django.utils import timezone
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vcec_bk.settings')
# Create your models here.
class UserCountStories(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.JSONField()
    
    
class ForumStories(models.Model):
    forum_id = models.ForeignKey(AddForum, on_delete=models.CASCADE)
    content = models.TextField()
    media_file = models.FileField(upload_to='forum/stories/media/', blank=True, null=True)
    thumbnail_media_file = models.FileField(upload_to='forum/stories/thumbnails/', blank=True, null=True)
    media_url = models.TextField(blank=True, null=True)
    thumbnail_media_url = models.TextField(blank=True, null=True)
    forum_tag = models.TextField(blank=False, null=False, default='')
    file_tag = models.TextField(blank=False, null=False, default='')
    upload_time = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
    
        if self.pk:
            existing_instance = ForumStories.objects.get(pk=self.pk)
            if existing_instance.media_file != self.media_file:
                # Delete the old image file
                if existing_instance.media_file:
                    path = existing_instance.media_file.path
                    if os.path.isfile(path):
                        os.remove(path)

            if existing_instance.thumbnail_media_file != self.thumbnail_media_file:
                # Delete the old thumbnail file
                if existing_instance.thumbnail_media_file:
                    path = existing_instance.thumbnail_media_file.path
                    if os.path.isfile(path):
                        os.remove(path)

        if self.media_file:
            
            if self.file_tag == 'img':
                self.media_url = f"forum/stories/media/{self.id}/file/"


        if self.thumbnail_media_file:
            self.thumbnail_media_url = f"forum/stories/thumbnails/{self.id}/thumbnail/"
            
                    
        super(ForumStories, self).save(*args, **kwargs)

