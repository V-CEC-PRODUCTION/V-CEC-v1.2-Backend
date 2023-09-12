from django.urls import path
from .views import *

urlpatterns = [
    path('create-event/',create_event,name='create-form'),
    path('delete-event/<int:pk>/',delete_event,name="delete-event"),
    path('get-event/',get_events,name="get-event"),
    path('update-event/<int:id>/',update_event,name='update-form'),
    path('cec/api/events/<int:pk>/file/',image_file,name='forum_events'),
    path('cec/api/events/<int:pk>/thumbnail/',thumbnail_file,name='forum_events'),
]
