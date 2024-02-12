from django.db import models, connection



class forumEvents(models.Model):
    title = models.TextField()
    content = models.TextField(blank=True,null=True)
    poster_image = models.ImageField(upload_to='forum/events/posters/')
    poster_image_url=models.TextField(blank=True,null=True) 
    thumbnail_poster_image = models.ImageField(upload_to='forum/events/thumbnails/', blank=True, null=True) 
    thumbnail_poster_image_url=models.TextField(blank=True,null=True) 
    register_button_link = models.TextField(default='vcec_form',blank=True,null=True)
    whatsapp_link = models.TextField(default='')
    status = models.CharField(max_length=10,default='Upcoming')
    publish_date = models.DateTimeField(auto_now_add=True)
    published_by = models.CharField(max_length=100)
    hashtags = models.TextField(blank=True,null=True)
    event_date=models.CharField(max_length=15,default='')

        
    def save(self, *args, **kwargs):
        if self.poster_image:
            self.poster_image_url = f"forum/events/cec/api/events/{self.id}/file/"
        if self.thumbnail_poster_image:
            self.thumbnail_poster_image_url = f"forum/events/cec/api/events/{self.id}/thumbnail/"

        super().save(*args, **kwargs)
    
    
class Registration(models.Model):
    name = models.TextField()
    event_id = models.ForeignKey(forumEvents, on_delete=models.CASCADE) 
    semester = models.CharField(max_length=10)
    division = models.CharField(max_length=10)
    email = models.TextField()
    phone_no = models.TextField()
    gender = models.TextField(default='Other')
    


class LikeEvent(models.Model):
    event_id = models.ForeignKey(forumEvents, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100,default='',unique=True)
    name = models.TextField()
    is_liked=models.BooleanField(default=False)
    views=models.BooleanField(default=True)



    
def create_dynamic_models(model_names):
    base_models = [LikeEvent, Registration]

    for base_model, new_model_name in zip(base_models, model_names):
        # Check if the new model name is a valid identifier
        if not new_model_name.isidentifier():
            print(f"Invalid model name: {new_model_name}")
            continue

        app_label = base_model._meta.app_label

        # Create a dictionary of field names and their corresponding field objects
        fields = {
            field.name: field.clone() for field in base_model._meta.fields
        }

        fields['__module__'] = app_label

        # Create the dynamic model class
        dynamic_model = type(new_model_name, (models.Model,), fields)

        # Create the database table for the dynamic model
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(dynamic_model)


def create_tables(app_name,unique_id):
    model_names = [app_name +"_"+ str(unique_id)+'_likes', app_name+"_"+str(unique_id)+'_registration']
    create_dynamic_models(model_names)
# def create_like_event_model(event):
#     class_name = f'LikeEvent{event.id}'
#     return type(class_name, (LikeEvent,), {
#         'event': models.ForeignKey(forumEvents, on_delete=models.CASCADE, default=event),
#     })
    
    
# def create_event_registration_model(event):
#     class_name = f'EventRegistration{event.id}'
#     return type(class_name, (Registration,), {
#         'event': models.ForeignKey(forumEvents, on_delete=models.CASCADE, default=event),
#     })
