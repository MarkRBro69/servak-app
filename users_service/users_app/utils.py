import logging

import requests
from django.core.cache import cache
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, TokenBackendError

from users_app.serializers import UserSerializer
from users_app.services import UserService
from users_service.settings import SECRET_KEY
from users_service.cluster_settings import USERS_SERVICE_URL

logger = logging.getLogger('logger')


def get_user(access_token):
    try:
        token_backend = TokenBackend(algorithm='HS256', signing_key=SECRET_KEY)
        decoded_token = token_backend.decode(access_token, verify=True)
        user_id = decoded_token.get('user_id')
        user_data = cache.get(f'auth_user_{user_id}')
        logger.debug(f'get_user: User from cache: {user_data}')
        if not user_data:
            user = UserService.get_user(user_id)
            serialized_user = UserSerializer(user)
            user_data = serialized_user.data
            logger.debug(f'get_user: User from db: {user_data}')
            cache.set(f'auth_user_{user_id}', user_data, timeout=60*60)
        return user_data
    except (TokenError, TokenBackendError) as e:
        logger.debug(f'Error: {e}')
        return None


def set_tokens(response, uat, urt):
    response.set_cookie('uat', uat, httponly=True, secure=True, samesite='Lax')
    response.set_cookie('urt', urt, httponly=True, secure=True, samesite='Lax')
    return response


def get_auth_user(request):
    cookies = {}
    uat = request.COOKIES.get('uat')
    urt = request.COOKIES.get('urt')
    if uat:
        cookies['uat'] = uat

    if urt:
        cookies['urt'] = urt

    logger.debug(f'get_auth_user: {cookies}')

    url = f'http://{USERS_SERVICE_URL}/api/usr/get_authenticated_user/'
    user_data = requests.get(url, cookies=cookies)

    logger.debug(f'get_auth_user: {user_data.status_code}')

    auth_user, uat, urt = unpack_auth_user(user_data)

    return auth_user, uat, urt


def unpack_auth_user(response_data):
    if response_data.status_code == 200:
        data = response_data.json()
        user = data.get('user')
        new_uat = data.get('uat')
        new_urt = data.get('urt')
        return user, new_uat, new_urt

    else:
        return None, None, None
