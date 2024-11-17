from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from users_kafka_module.async_kafka_producer import produce_profile_notification

from users_app.forms import *
from users_app.services import *
from users_app.utils import set_tokens, get_auth_user, get_user
from users_service.cluster_settings import USERS_SERVICE_URL

logger = logging.getLogger('users_service')


def home(request):
    if request.method == 'GET':
        context = {'title': 'Home page'}
        return render(request, 'users_app/home.html', context)

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def user_register(request):
    if request.method == 'GET':
        form = RegisterUserForm()
        context = {
            'title': 'Registration',
            'form': form,
            'button_name': 'Register'
        }
        return render(request, 'users_app/base_form.html', context)

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()

            login_data = {
                'username': form.cleaned_data.get('username'),
                'password': form.cleaned_data.get('password1')
            }

            login_form = AuthenticationForm(request, data=login_data)
            response = UserService.user_login(request, login_form)
            return response
        else:
            context = {
                'title': 'Registration',
                'form': form,
                'button_name': 'Register'
            }
            return render(request, 'users_app/base_form.html', context)

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def user_login(request):
    logger.debug('user login view')
    if request.method == 'GET':
        form = AuthenticationForm()
        context = {
            'title': 'Login',
            'form': form,
            'button_name': 'Login'
        }
        return render(request, 'users_app/base_form.html', context)

    if request.method == 'POST':
        logger.debug('getting auth form')
        form = AuthenticationForm(request, data=request.POST)
        logger.debug(form)
        response = UserService.user_login(request, form)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


@api_view(['POST'])
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        response = redirect('home')
        response.delete_cookie('uat')
        response.delete_cookie('urt')
        response['Logout'] = 'true'
        return response


@api_view(['GET'])
def user_desktop(request):
    if request.method == 'GET':
        auth_user, uat, urt = get_auth_user(request)
        context = {
            'title': 'Desktop',
            'auth_user': auth_user
        }

        if request.headers.get('Authorization'):
            logger.debug(f'user_desktop: Auth headers: {request.headers["Authorization"]}')
        logger.debug(f'user_desktop: Request user: {request.user}')
        logger.debug(f'user_desktop: Auth user: {auth_user}')

        response = render(request, 'users_app/user_desktop.html', context)

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response


@api_view(['GET'])
def profile_detail(request, user_id):
    if request.method == 'GET':
        auth_user, uat, urt = get_auth_user(request)
        profile, followers, followings = UserService.get_user_profile_detail(user_id)
        notifications = Notification.objects(user_id=user_id)

        context = {
            'title': 'Profile',
            'auth_user_id': auth_user['id'],
            'profile': profile,
            'followers': followers,
            'followings': followings,
            'notifications': notifications
        }

        response = render(request, 'users_app/profile_detail.html', context)

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response


@api_view(['GET', 'POST'])
def profile_update(request, user_id):
    auth_user, uat, urt = get_auth_user(request)

    if auth_user['id'] != user_id:
        response = Response({'message': 'Access denied'}, status=403)

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response

    profile = UserService.get_user_profile(user_id)

    if request.method == 'GET':
        form = ProfileForm(instance=profile)
        context = {
            'title': 'Update profile',
            'form': form,
            'button_name': 'Update'
        }
        response = render(request, 'users_app/base_form.html', context)

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            produce_profile_notification(user_id)
            response = redirect('desktop')
        else:
            context = {
                'title': 'Update profile',
                'form': form,
                'button_name': 'Update'
            }
            response = render(request, 'users_app/base_form.html', context)

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response


@api_view(['POST'])
def follow_user(request, user_to_follow_id):
    if request.method == 'POST':
        auth_user, uat, urt = get_auth_user(request)

        logger.debug(auth_user)
        logger.debug(uat)
        logger.debug(urt)
        logger.debug(f'Auth user id: {auth_user["id"]}')

        UserService.create_subscription(auth_user['id'], user_to_follow_id)

        response = redirect('profile_detail', auth_user['id'])

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response


@api_view(['POST'])
def unfollow_user(request, user_to_unfollow_id):
    if request.method == 'POST':
        auth_user, uat, urt = get_auth_user(request)

        UserService.delete_subscription(auth_user['id'], user_to_unfollow_id)

        response = redirect('profile_detail', auth_user['id'])

        if uat is not None:
            response = set_tokens(response, uat, urt)

        return response


@api_view(['GET'])
def get_authenticated_user(request):
    if request.headers.get('Authorization'):
        logger.debug(f'get_authenticated_user: Auth headers: {request.headers["Authorization"]}')
    else:
        logger.debug('get_authenticated_user: No authorization token in header')

    logger.debug(f'get_authenticated_user: Request user: {request.user}')

    uat = request.COOKIES.get('uat')
    if uat:
        user_data = get_user(uat)

        if user_data:
            response_data = {
                'user': user_data,
            }
            response = Response(response_data, status=200)
            return response
        else:
            url = f'http://{USERS_SERVICE_URL}/api/token/refresh/'
            urt = request.COOKIES.get('urt')
            data = {'refresh': urt}

            logger.debug(f'get_authenticated_user: Data: {data}')

            refreshed_tokens = requests.post(url, data=data)

            logger.debug(f'get_authenticated_user: Response status code: {refreshed_tokens.status_code}')

            if refreshed_tokens.status_code == 200:
                tokens = refreshed_tokens.json()
                new_uat = tokens.get('access')
                new_urt = tokens.get('refresh')
                user_data = get_user(new_uat)
                response_data = {
                    'user': user_data,
                    'uat': new_uat,
                    'urt': new_urt,
                }

                response = Response(response_data, status=200)
                return response

    else:
        response_data = {'message': 'No access token, Unauthorized'}
        return Response(response_data, status=401)


@api_view(['GET'])
def notification_detail(request, notification_id):
    if request.method == 'GET':
        notification = Notification.objects.get(id=notification_id)
        context = {
            'title': f'Notification: {notification_id}',
            'notification': notification,
        }
        return render(request, 'users_app/notification_detail.html', context)
