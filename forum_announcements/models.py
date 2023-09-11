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
            self.poster_image_url = f"forum/announcements/cec/api/announcements/{self.id}/{self.id}/file/"
        if self.thumbnail_poster_image:
            self.thumbnail_poster_image_url = f"forum/announcements/cec/api/announcements/{self.id}/thumbnail/"

        super().save(*args, **kwargs)
    
class LikeAnnouncement(models.Model):
    event_id = models.ForeignKey(forumAnnouncements, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,blank=True,null=True)
    name = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

def create_dynamic_model(new_model_name,unique_id):

    if not new_model_name.isidentifier():
        print(f"Invalid model name: {new_model_name}")
        return False
    app_label = LikeAnnouncement._meta.app_label
    # Create a dictionary of field names and their corresponding field objects
    fields = {
        field.name: field.clone() for field in LikeAnnouncement._meta.fields
    }
    fields['__module__'] = app_label

    fields['event_id']=models.IntegerField(default=unique_id)
    # Create the dynamic model class
    dynamic_model = type(new_model_name, (models.Model,), fields)
    # Create the database table for the dynamic model
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(dynamic_model)
    return True
