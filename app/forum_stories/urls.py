from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.AddForumStories.as_view(), name='add-forum-stories'),
    path('delete/<str:pk>/', views.DeleteForumStories.as_view(), name='delete-forum-stories'),
    path('user/see/story/mark/', views.SeeStories.as_view(), name='see-stories'),
    path('get/status/', views.GetForumStories.as_view(), name='get-forum-stories'),
    path('media/<str:pk>/file/', views.ImageFile.as_view(), name='image-file'),  
    path('media/<str:pk>/thumbnail/', views.ThumbnailFile.as_view(), name='image-thumbnail'),
    path('video/media/<str:pk>/file/', views.StreamVideo.as_view(), name='stream-video'),
    path('get/user/seen/count/', views.GetUserStoriesStatus.as_view(), name='get-user-stories-status'),
]
