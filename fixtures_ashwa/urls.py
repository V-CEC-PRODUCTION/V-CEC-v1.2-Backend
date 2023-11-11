from django.urls import path
from . import views

urlpatterns = [
    path('result/all/', views.FixturesView.as_view(), name='fixtures'),
]