from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'chat/(?P<room_id>\d+)/$', views.chat_room, name='chat_room'),
]
