from django.urls import path
from . import views


urlpatterns = [
    path("ktu", views.ktu_announcements_scrap),
]
