from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'chat/$', views.enter_your_chat, name='enter_your_chat'),
    re_path(r'chat/(?P<room_id>\d+)/$', views.enter_to_chat, name='enter_to_chat'),
]
