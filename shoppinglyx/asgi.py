# """
# ASGI config for shoppinglyx project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
# """

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from django.core.asgi import get_asgi_application

from app.consumers import OrderProgress

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoppinglyx.settings")
# application = get_asgi_application()

ws_pattern = [
    path("ws/order/<int:uid>", OrderProgress.as_asgi()),
]
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(ws_pattern)),
    },
)
