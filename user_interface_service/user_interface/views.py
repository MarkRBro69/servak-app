import json
import os

import requests
from django.http import HttpResponse
from django.shortcuts import redirect

from user_interface_service.settings import USERS_SERVICE_URL, POSTS_SERVICE_URL


def proxy_to_users_service(request, path):
    path = f'api/{path}'
    new_uat = None
    new_urt = None
    cookie_update_flag = False
    srv_url = path_parser(path)
    service_url = f'http://{srv_url}/{path}/'
    headers = {'Host': '127.0.0.1'}
    cookies = request.COOKIES
    params = request.GET.dict()

    csrf_token = request.headers.get('X-CSRFToken')
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
        cookies['csrftoken'] = csrf_token

    uat = cookies.get('uat')
    if uat:
        headers['Authorization'] = f'Bearer {uat}'

    response = proxy_request(request, service_url, headers, cookies, params)

    try:
        json_content = response.json()
        content_code = json_content.get('code')
        if content_code and content_code == 'token_not_valid':
            new_uat, new_urt = proxy_token_update(request)

            if new_uat is not None:
                cookie_update_flag = True

                headers['Authorization'] = f'Bearer {new_uat}'

                cookies['uat'] = new_uat
                cookies['urt'] = new_urt

                response = proxy_request(request, service_url, headers, cookies, params)

            else:
                response = redirect(f'http://{USERS_SERVICE_URL}/api/login/')

    except json.JSONDecodeError:
        pass
    except Exception as e:
        pass

    http_response = HttpResponse(
        response.content,
        status=response.status_code,
        content_type=response.headers.get('Content-Type')
    )

    update_page_header = response.headers.get('Update-Page')
    if update_page_header == 'true':
        http_response['Location'] = request.headers.get('Referer')
        http_response.status_code = 301
    else:
        http_response['Location'] = response.headers.get('Location')

    for key, value in response.headers.items():
        if key.lower() != 'set_cookie':
            http_response[key] = value

    for cookie in response.cookies:
        http_response.set_cookie(
            key=cookie.name,
            value=cookie.value,
            max_age=cookie.expires,
            httponly=cookie.has_nonstandard_attr('HttpOnly'),
            secure=cookie.secure,
            samesite='Lax'
        )

    if cookie_update_flag:
        http_response.set_cookie(
            key='uat',
            value=new_uat,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        http_response.set_cookie(
            key='urt',
            value=new_urt,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

    if http_response.get('Logout') == 'true':
        http_response.delete_cookie('uat')
        http_response.delete_cookie('urt')

    return http_response


def proxy_request(request, service_url, headers, cookies, params):
    response = None
    if request.method == 'GET':
        response = requests.get(service_url, headers=headers, cookies=cookies, params=params,
                                allow_redirects=False)

    elif request.method == 'POST':
        csrftoken = request.POST.get('csrfmiddlewaretoken')
        if csrftoken:
            cookies['csrftoken'] = csrftoken
        response = requests.post(
            service_url,
            data=request.POST,
            headers=headers,
            cookies=cookies,
            files=request.FILES,
            allow_redirects=False)

    elif request.method == 'DELETE':
        response = requests.delete(service_url, data=request.POST, headers=headers, cookies=cookies,
                                   allow_redirects=False)

    return response


def proxy_token_update(request):
    new_uat = None
    new_urt = None
    service_url = f'http://{USERS_SERVICE_URL}/api/token/refresh/'
    data = {}
    urt = request.COOKIES.get('urt')
    if urt:
        data['refresh'] = urt

    response = requests.post(service_url, data=data)

    if response.status_code == 200:
        tokens = response.json()
        new_uat = tokens['access']
        new_urt = tokens['refresh']

    return new_uat, new_urt


def headers_cookie_parser(data):
    set_cookie_header = data.headers.get('Set-Cookie')

    if set_cookie_header:
        cookies = set_cookie_header.split(',')

        for index, cookie in enumerate(cookies):
            print(f"{index}: {cookie.strip()}")

    for cookie in data.cookies:
        print(cookie)


def path_parser(path):
    if os.getenv('RUNNING_IN_DOCKER'):
        usr_url = 'users_service:8002'
        pst_url = 'posts_service:8003'
    else:
        usr_url = USERS_SERVICE_URL
        pst_url = POSTS_SERVICE_URL

    # usr_url = USERS_SERVICE_URL
    # pst_url = POSTS_SERVICE_URL

    path_code = path[:7]
    service_url = ''
    if path_code == 'api/usr':
        service_url = usr_url
    elif path_code == 'api/pst':
        service_url = pst_url
    elif path_code == 'favicon':
        service_url = usr_url
    elif path_code == 'captcha':
        service_url = usr_url

    return service_url
