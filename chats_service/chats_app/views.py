from django.shortcuts import render, redirect
from django.urls import reverse

from chats_app.kafka_producer import produce_chat_notification
from chats_app.utils import *


@auth_user
def enter_your_chat(request, user=None):
    user_id = user['id']
    room_id = get_room_id(user_id)
    url = reverse('enter_to_chat', args=[room_id])
    return redirect(f'{url}?user_id={user_id}')


def enter_to_chat(request, room_id):
    user_service_url = USERS_SERVICE_URL
    user_id = request.GET.get('user_id')
    params = {'user_id': user_id}
    url = f'http://{user_service_url}/api/usr/get_user_connections/'
    logger.debug(f'enter_to_chat: user_id: {user_id}')
    logger.debug(f'enter_to_chat: url: {url}')

    response = requests.get(url, params=params)
    logger.debug(f'enter_to_chat: status_code: {response.status_code}')
    data = response.json()

    context = {
        'room_id': room_id,
        'followers': data.get('followers'),
        'followings': data.get('followings'),
    }
    return render(request, 'chats_app/chat_room.html', context)


@auth_user
def send_invite(request, user_id, user_to_invite, room_id):
    produce_chat_notification(user_id, user_to_invite, room_id)
    return
