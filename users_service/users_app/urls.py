from django.urls import path

from users_app.views import *

urlpatterns = [
    # User
    path('', home, name='home'),
    path('desktop/', user_desktop, name='desktop'),
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('profile/<int:user_id>/', profile_detail, name='profile_detail'),
    path('profile/<int:user_id>/update/', profile_update, name='profile_update'),
    path('follow/<int:user_to_follow_id>/', follow_user, name='follow_user'),
    path('unfollow/<int:user_to_unfollow_id>/', unfollow_user, name='unfollow_user'),
    path('profile/notification/<str:notification_id>/', notification_detail, name='notification_detail'),

    # API
    path('get_authenticated_user/', get_authenticated_user, name='get_authenticated_user')
]
