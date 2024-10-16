from django.urls import path
from .views import *
from .tasks import *

urlpatterns=[
    path('create-timetable/excel/',create_timetables,name="post_timetable"),
    path('create-timetable/',create_timetable,name="post_timetable"),
    path('get-timetable/admin/',get_timetables,name="get_timetables"),
    path('get-timetable/client/',get_clienttimetables,name="get_clienttimetables"),
    path('get-timetable/current/',GetCurrentCode.as_view(),name="get_currentcodetime"),
    path('delete-timetable/<str:semester>/<str:division>/<int:day>/', delete_timetable, name='delete_timetable'),
    path('delete-timetable/<str:semester>/<str:division>/', delete_timetable, name='delete_timetablesemdiv'),
    path('delete-timetable/<str:semester>/', delete_timetable, name='delete_timetablesem'),
    path('update-timetable/<str:semester>/<str:division>/<int:day>/', update_timetable, name='update_timetable'),



    path('auto/update/time-table', AutoTimeTableSystem.as_view(), name='auto-update-timetable'),

]