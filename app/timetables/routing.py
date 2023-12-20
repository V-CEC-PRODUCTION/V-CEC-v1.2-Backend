from django.urls import path
from timetables import consumers
 
# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
    path('timetable/cec/realtimeupdate/', consumers.TimeTableConsumer.as_asgi()),
]
