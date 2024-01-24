from django.urls import path
from .views import *

urlpatterns = [
    path('images/', get_all_images.as_view(), name='image-list'),
    path('images/<int:pk>/', get_image_detail, name='image-detail'),
    path('images/create/', create_image, name='image-create'),
    path('images/<int:pk>/delete/', delete_image, name='image-delete'),
    path('api/images/<int:pk>/file/', image_file, name='image-file'),
    path('api/images/<int:pk>/thumbnail/', thumbnail_file, name='thumbnail-file')
]
