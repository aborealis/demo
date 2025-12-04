"""Channels routing for websockets"""
from channels.routing import URLRouter

websocket_urlpatterns = [
    # Add websocket URL patterns here, e.g.:
    # re_path(r"ws/somepath/", consumers.MyConsumer.as_asgi()),
]

websocket_application = URLRouter(websocket_urlpatterns)
