import logging

from asgiref.sync import sync_to_async
from django.shortcuts import render, get_object_or_404, redirect

from users_app.models import *

import requests

from users_app.mongomodels import Notification

logger = logging.getLogger('users_service')


class UserService:
    @staticmethod
    def user_login(request, form):
        context = {
            'title': 'Login',
            'form': form,
            'button_name': 'Login'
        }

        logger.debug(form)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            data = {
                'username': username,
                'password': password,
            }

            url = 'http://127.0.0.2:8002/api/token/'
            logger.debug(data)
            response = requests.post(url, data=data)
            logger.debug(response.status_code)
            logger.debug(response.text)

            if response.status_code == 200:
                tokens = response.json()
                uat = tokens.get('access')
                urt = tokens.get('refresh')

                response = redirect('desktop')
                response.set_cookie('uat', uat, httponly=True, secure=True, samesite='Lax')
                response.set_cookie('urt', urt, httponly=True, secure=True, samesite='Lax')

                return response

            else:
                return render(request, 'users_app/base_form.html', context)

        else:
            return render(request, 'users_app/base_form.html', context)

    @staticmethod
    def get_user(user_id):
        user = get_object_or_404(User, id=user_id)
        return user

    @staticmethod
    def get_user_profile(user_id):
        profile = get_object_or_404(Profile.objects.select_related('user'), user=user_id)
        return profile

    @staticmethod
    def get_user_profile_detail(user_id):
        profile = UserService.get_user_profile(user_id)
        followers = UserService.get_user_followers(profile)
        followings = UserService.get_user_followings(profile)
        return profile, followers, followings

    @staticmethod
    def create_subscription(current_user_id, user_to_follow_id):
        current_profile = UserService.get_user_profile(current_user_id)
        user_to_follow_profile = UserService.get_user_profile(user_to_follow_id)
        Subscription.objects.get_or_create(follower=current_profile, followed=user_to_follow_profile)

    @staticmethod
    def delete_subscription(current_user_id, user_to_unfollow_id):
        current_profile = UserService.get_user_profile(current_user_id)
        user_to_unfollow_profile = UserService.get_user_profile(user_to_unfollow_id)
        Subscription.objects.filter(follower=current_profile, followed=user_to_unfollow_profile).delete()

    @staticmethod
    def get_user_followers(profile):
        followers = Subscription.objects.filter(followed=profile).select_related('follower__user')
        return followers

    @staticmethod
    def get_user_followings(profile):
        followings = Subscription.objects.filter(follower=profile).select_related('followed__user')
        return followings

    @staticmethod
    async def send_post_notifications(user_id, message):
        profile = await sync_to_async(UserService.get_user_profile)(user_id)
        followers = await sync_to_async(UserService.get_user_followers)(profile)
        logger.debug(f'Sending post notifications')
        logger.debug(profile)

        async for f in followers:
            logger.debug(f'user id: {f.follower.user.id}')
            notification = Notification(
                user_id=f.follower.user.id,
                message=message,
                type='post_notification',
                status='unread',
            )
            await sync_to_async(notification.save)()
            logger.debug(f'Notification created: {notification.id}')
