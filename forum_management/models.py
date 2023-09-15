from django.db import models
import os

class AddForum(models.Model):
    forum_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, default='No display name')
    forum_description = models.TextField(default='No description')
    email_id = models.TextField()
    forum_role_name = models.CharField(max_length=100)
    forum_image = models.ImageField(upload_to='forum/management/images/')
    thumbnail_forum_image = models.ImageField(upload_to='forum/management/thumbnails/', blank=True, null=True)
    logged_in = models.BooleanField(default=False)
    image_url = models.TextField(blank=True, null=True)
    thumbnail_url = models.TextField(blank=True, null=True)

        
    def save(self, *args, **kwargs):
        if self.pk:
            existing_instance = AddForum.objects.get(pk=self.pk)
            if existing_instance.forum_image != self.forum_image:
                # Delete the old image file
                if existing_instance.forum_image:
                    path = existing_instance.forum_image.path
                    if os.path.isfile(path):
                        os.remove(path)
                        
                        
            if existing_instance.thumbnail_forum_image != self.thumbnail_forum_image:
                # Delete the old image file
                if existing_instance.thumbnail_forum_image:
                    path = existing_instance.thumbnail_forum_image.path
                    if os.path.isfile(path):
                        os.remove(path)

        if self.forum_image:
            self.image_url = f"forum/management/images/{self.id}/file/"
        if self.thumbnail_forum_image:
            self.thumbnail_url = f"forum/management/thumbnails/{self.id}/thumbnail/"

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