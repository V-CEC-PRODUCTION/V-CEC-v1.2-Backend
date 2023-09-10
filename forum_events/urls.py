from django.urls import path
from .views import *

urlpatterns = [
    path('create-form/',create_form,name='create-form'),
    path('delete-event/<int:pk>',delete_event,name="delete-event"),
    path('get-event/',get_events,name="get-event")
    path('update-form/<int:id>/',update_form,name='update-form'),
    path('cec/api/events/<int:pk>/file/',image_file,name='forum_events'),
    path('cec/api/events/<int:pk>/thumbnail/',thumbnail_file,name='forum_events'),
]
