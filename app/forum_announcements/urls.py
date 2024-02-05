from django.urls import path
from .views import *

urlpatterns =[
    path('create-announcement/',create_announcement,name='create-form'),
    path('cec/api/announcements/<int:pk>/file/',image_file,name='forum_events'),
    path('cec/api/announcements/<int:pk>/thumbnail/',thumbnail_file,name='forum_events'),
    path('update-announcement/<int:id>/',update_announcement,name='update-form'),
    path('delete-announcement/<int:pk>/',delete_announcement,name="delete-event"),
    path('get-announcement/',GetAllAnnouncementsClientSide.as_view(),name='get-announcements'),
    path('get-announcement/<int:id>/',GetAnnoucement.as_view(),name='get-announcement-by-id'),
]