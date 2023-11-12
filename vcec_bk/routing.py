from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from live_update_board import routing as live_update_board_routing
from timetables import routing as timetables_routing
from django.core.asgi import get_asgi_application

websocket_urlpatterns = (
    live_update_board_routing.websocket_urlpatterns +
    timetables_routing.websocket_urlpatterns
)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            websocket_urlpatterns,
        )
    ),
})
