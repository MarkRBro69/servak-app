from django.shortcuts import render, redirect

from chats_app.kafka_producer import produce_chat_notification
from chats_app.utils import *


@auth_user
def enter_your_chat(request, user_id=None):
    room_id = get_room_id(user_id)
    return redirect('enter_to_chat', user_id, user_id, room_id)


@auth_user
def enter_to_chat(request, admin_user=None, user_id=None, room_id=None):
    context = {
        'admin_user': admin_user,
        'auth_user': user_id,
        'room_id': room_id,
    }
    render(request, 'chats_app/chat_room.html', context)


@auth_user
def send_invite(request, user_id, user_to_invite, room_id):
    produce_chat_notification(user_id, user_to_invite, room_id)
    return
