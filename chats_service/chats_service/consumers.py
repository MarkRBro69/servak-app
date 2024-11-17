import json
from channels.generic.websocket import AsyncWebsocketConsumer

from chats_app.utils import get_auth_user


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room_group_name = None
        self.user_id = None
        self.user_group_name = None

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        uat = self.scope['cookies'].get('uat')
        urt = self.scope['cookies'].get('urt')
        self.user_id = get_auth_user(uat, urt)
        self.user_group_name = f'user_{self.user_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        message_type = text_data_json.get('type')

        if message_type == 'chat_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

        elif message_type == 'user_message':
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    'type': 'user_message',
                    'message': message,
                }
            )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'chat_message'
        }))

    async def user_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'user_message'
        }))
