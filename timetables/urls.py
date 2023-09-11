from django.urls import path
from .views import *

urlpatterns=[
    path('create-timetable/excel/',create_timetables,name="post_timetable"),
    path('create-timetable/',create_timetable,name="post_timetable"),
]