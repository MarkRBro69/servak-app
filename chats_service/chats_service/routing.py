from django.urls import re_path
from chats_service import consumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_id>\w+)/?$', consumers.ChatConsumer.as_asgi()),
]
