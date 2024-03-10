from django.urls import path
from . import views

urlpatterns = [
    path('create/season/', views.SeasonDetails.as_view(), name='create-season'),
    path('update/season/', views.SeasonDetails.as_view(), name='update-season'),
    path('get/seasons', views.SeasonDetails.as_view(), name='get-season'),
    path('delete/season/', views.SeasonDetails.as_view(), name='delete-season'),
    
    path('create/season/episode/', views.EpisodeDetails.as_view(), name='create-season-episode'),
    path('update/season/episode/', views.EpisodeDetails.as_view(), name='update-season-episode'),
    path('get/season/episodes', views.EpisodeDetails.as_view(), name='get-season-episode'),
    path('delete/season/episode/', views.EpisodeDetails.as_view(), name='delete-season-episode'),
    
    path('filter/seasons', views.SeasonFilterMethods.as_view(), name='filter-seasons'),
]