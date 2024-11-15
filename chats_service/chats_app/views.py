from django.shortcuts import render


def chat_room(request, room_id):
    return render(request, 'chats_app/chat_room.html', {'room_id': room_id})
