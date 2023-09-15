from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.AddForumStories.as_view(), name='add-forum-stories'),
]
