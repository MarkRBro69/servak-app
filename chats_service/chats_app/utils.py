import logging

import requests
import random
import string

from django_redis import get_redis_connection

from chats_service.cluster_settings import USERS_SERVICE_URL


logger = logging.getLogger('logger')


def get_room_id(user_id):
    rcache = get_redis_connection("default")
    logger.debug(f'get_room_id: user_id: {user_id}')
    if rcache.hexists('user_room_set', user_id):
        room_id = rcache.hget('user_room_set', user_id).decode()
    else:
        room_id = generate_unique_room_id()
        rcache.hset('user_room_set', user_id, room_id)
    logger.debug(f'get_room_id: room_id: {room_id}')
    return room_id


def generate_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def generate_unique_room_id():
    rcache = get_redis_connection("default")
    max_attempts = 100

    for _ in range(max_attempts):
        new_id = generate_id()

        if not rcache.sismember('room_set', new_id):
            rcache.sadd('room_set', new_id)
            logger.debug(f'generate_unique_room_id: new id generated: {new_id}')
            return new_id

    raise Exception('Unique id is not generated')


def add_csrf_token(request, headers):
    csrf_token = request.POST.get('csrftoken')
    headers['X-CSRFToken'] = csrf_token
    return headers


def get_authenticated_user(request):
    user = None
    new_uat = None
    new_urt = None

    headers = {'Host': '127.0.0.2'}
    cookies = {}
    uat = request.COOKIES.get('uat')
    urt = request.COOKIES.get('urt')

    if uat:
        cookies['uat'] = uat
    if urt:
        cookies['urt'] = urt

    usr_url = USERS_SERVICE_URL

    url = f'http://{usr_url}/api/usr/get_authenticated_user/'
    response_data = requests.get(url, headers=headers, cookies=cookies)
    if response_data.status_code == 200:
        data = response_data.json()
        user = data.get('user')
        new_uat = data.get('uat')
        new_urt = data.get('urt')

    return user, new_uat, new_urt


def get_auth_user(uat, urt):
    cookies = {
        'uat': uat,
        'urt': urt,
    }
    usr_url = USERS_SERVICE_URL
    url = f'http://{usr_url}/api/usr/get_authenticated_user/'
    response_data = requests.get(url, cookies=cookies)
    if response_data.status_code == 200:
        data = response_data.json()
        user = data.get('user')
        new_uat = data.get('uat')
        new_urt = data.get('urt')

        return user, new_uat, new_urt


def set_tokens(response, uat, urt):
    response.set_cookie('uat', uat, httponly=True, secure=True, samesite='Lax')
    response.set_cookie('urt', urt, httponly=True, secure=True, samesite='Lax')
    return response


def auth_user(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        user, uat, urt = get_authenticated_user(request)
        response = func(*args, user=user, **kwargs)
        if uat and urt:
            response = set_tokens(response, uat, urt)
        return response
    return wrapper


