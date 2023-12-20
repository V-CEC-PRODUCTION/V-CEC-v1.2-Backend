from django.urls import path
from live_update_board import consumers,consumers_team
 
# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
    path('all/team/score/board/realtimeupdate/', consumers.RealTimeConsumer.as_asgi()),
    path('<str:color>/team/score/board/realtimeupdate/', consumers_team.TeamRealTimeConsumer.as_asgi()),
]
