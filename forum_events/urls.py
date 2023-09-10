from django.urls import path
from .views import *

urlpatterns = [
    path('create-form/',create_forms,name='create-form'),
    path('delete-event/<int:pk>',delete_event,name="delete-event"),
    path('get-event/',get_events,name="get-event")]
