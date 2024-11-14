import os

import requests

from posts_service.settings import USERS_SERVICE_URL


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

    usr_url = 'users-service.servak-app.svc.cluster.local'

    url = f'http://{usr_url}/api/usr/get_authenticated_user/'
    response_data = requests.get(url, headers=headers, cookies=cookies)
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

