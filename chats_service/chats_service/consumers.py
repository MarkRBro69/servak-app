import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from chats_app.utils import get_auth_user


logger = logging.getLogger('logger')


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room_group_name = None
        self.user_id = None
        self.user_group_name = None

    async def connect(self):
        logger.debug('connect: start connect')
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        logger.debug(f'connect: room_group_name: {self.room_group_name}')

        uat = self.scope['cookies'].get('uat')
        urt = self.scope['cookies'].get('urt')
        user, _, _ = get_auth_user(uat, urt)
        self.user_id = user['id']
        self.user_group_name = f'user_{self.user_id}'

        logger.debug(f'connect: user_group_name: {self.user_group_name}')

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

        logger.debug(f'disconnect: disconnected')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        message_type = text_data_json.get('type')

        logger.debug(f'receive: message received: {message}, {message_type}')

        if message_type == 'chat_message':
            logger.debug(f'receive: chat_message sent')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message
                }
            )

        elif message_type == 'user_message':
            logger.debug(f'receive: user_message sent')
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    'type': 'user.message',
                    'message': message,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        logger.debug(f'chat_message: message: {message}')

        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'chat_message'
        }))

    async def user_message(self, event):
        message = event['message']
        logger.debug(f'user_message: message: {message}')

        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'user_message'
        }))
