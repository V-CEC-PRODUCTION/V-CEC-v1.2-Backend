from django.urls import path
from .views import *

urlpatterns=[
    path('create-timetable/excel/',create_timetables,name="post_timetable"),
    path('create-timetable/',create_timetable,name="post_timetable"),
    path('get-timetable/admin/',get_timetables,name="get_timetables"),
    path('get-timetable/client/',get_clienttimetables,name="get_clienttimetables"),
    path('get-timetable/current/<int:id>/',get_currentcodetime,name="get_currentcodetime")


]