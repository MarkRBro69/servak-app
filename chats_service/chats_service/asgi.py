import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chats_service.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chats_service.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(
            chats_service.routing.websocket_urlpatterns
        )
    ),
})
