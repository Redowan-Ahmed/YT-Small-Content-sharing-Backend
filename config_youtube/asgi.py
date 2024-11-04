

import os
import django
from django.core.asgi import get_asgi_application
from django.urls import re_path, path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channel.consumers import LikeCountConsumer, SimpleConsumer
from .middleware import JWTAuthMiddleware
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config_youtube.settings')

# django.setup()

django_asgi_app = get_asgi_application()

# application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter([
                path("like-count/<str:room_name>/", LikeCountConsumer.as_asgi()),
                path("like/", SimpleConsumer.as_asgi()),
            ])
        ),
    ),

})