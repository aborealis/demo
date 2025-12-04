"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

from django.conf import settings
from django.core.asgi import get_asgi_application
from channels.security.websocket import OriginValidator
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from mysite.routing import websocket_application


# Standard Django ASGI application for HTTP
django_asgi_app = get_asgi_application()

# ProtocolTypeRouter will route between "http" and "websocket" protocols.
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": OriginValidator(
        AuthMiddlewareStack(websocket_application),
        settings.CORS_ALLOWED_ORIGINS,
    )
})
