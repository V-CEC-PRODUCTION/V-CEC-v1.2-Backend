from django.urls import path
from .views import *

urlpatterns = [
    path('images/', get_all_files.as_view(), name='file-list'),
    path('files/<int:pk>/', get_file_detail, name='file-detail'),
    path('files/create/', post_file, name='file-create'),
    path('files/delete/<int:pk>', delete_file, name='file-delete'),
    path('files/videos/get/<int:pk>', get_detail_video, name='get-detail-video'),
    path('api/media/files/video/<int:pk>',stream_video, name='stream-video'),
    path('api/media/<int:pk>/file/', media_file, name='open-file'),
    path('api/media/<int:pk>/thumbnail/', thumbnail_file, name='open-thumbnail-file')
]
