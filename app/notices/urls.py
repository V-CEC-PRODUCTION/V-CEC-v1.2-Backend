from django.urls import path
from . import views
from . import tasks

urlpatterns = [
    path("ktu", views.ktu_announcements_scrap),
    path("task/scrap/ktu", tasks.KTUWebScrapTask.as_view()),
]
