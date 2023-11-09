from django.urls import path
from . import views

urlpatterns = [
    path('team_score/update/', views.TeamScoreList.as_view(), name='team_score_update'),
    path('scores/page/', views.scores, name='scores'),
    path('pusher/front/', views.pusher_front, name='pusher_front'),
]