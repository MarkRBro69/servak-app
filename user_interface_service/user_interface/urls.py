from django.urls import path

from user_interface.views import *

urlpatterns = [
    path('api/<path:path>/', proxy_to_users_service),
]
