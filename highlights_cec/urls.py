from django.urls import path
from .views import *

urlpatterns = [
    path('images/', get_all_highlights, name='image-list'),
    path('images/<int:pk>/', get_highlight_detail, name='image-detail'),
    path('images/create/', create_highlight, name='highlight-create'),
    path('images/<int:pk>/delete/', delete_highlight, name='image-delete'),
    path('api/images/<int:pk>/file/', image_file, name='image-file'),
    path('api/images/<int:pk>/thumbnail/', thumbnail_file, name='thumbnail-file')
]