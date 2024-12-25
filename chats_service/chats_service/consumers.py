import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from chats_app.utils import get_auth_user, check_room_owner, get_room_owner

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
        uat = self.scope['cookies'].get('uat')
        urt = self.scope['cookies'].get('urt')
        user, _, _ = get_auth_user(uat, urt)
        self.user_id = user['id']
        self.user_group_name = f'user_{self.user_id}'
        logger.debug(f'connect: user_group_name: {self.user_group_name}')
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        is_room_owner = check_room_owner(user['id'], self.room_id)
        if is_room_owner:
            self.room_group_name = f"chat_{self.room_id}"
            logger.debug(f'connect: room_group_name: {self.room_group_name}')
            await self.channel_layer.group_add(
                self.room_group_name,
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
        from_user = text_data_json.get('from_user')

        logger.debug(f'receive: message received: {message}, {message_type}')

        if message_type == 'chat_message':
            logger.debug(f'receive: chat_message sent')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_event',
                    'message': message
                }
            )

        elif message_type == 'connection_request':
            logger.debug(f'receive: connection_request sent')
            room_owner = get_room_owner(self.room_id)
            if str(room_owner) == str(self.user_id):
                return
            else:
                owner_group_name = f'user_{room_owner}'
                await self.channel_layer.group_send(
                    owner_group_name,
                    {
                        'type': 'connection_request_event',
                        'message': self.user_id,
                    }
                )

        elif message_type == "connection_response":
            logger.debug(f'receive: connection_response sent')
            if message == 'true':
                await self.channel_layer.group_send(
                    f"user_{from_user}",
                    {
                        "type": "connection_granted_event",
                        "message": self.room_group_name
                    }
                )
            else:
                await self.channel_layer.group_send(
                    f"user_{from_user}",
                    {
                        "type": "connection_denied_event"
                    }
                )

    async def chat_message_event(self, event):
        message = event['message']
        logger.debug(f'chat_message: message: {message}')

        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'chat_message'
        }))

    async def connection_request_event(self, event):
        from_user = event['message']
        await self.send(text_data=json.dumps({
            "type": "connection_request",
            "message": from_user
        }))

    async def connection_granted_event(self, event):
        room_name = event['message']
        self.room_group_name = room_name
        await self.channel_layer.group_add(
            room_name,
            self.channel_name
        )

        await self.send(text_data=json.dumps({
            "type": "connection_granted",
            "message": room_name
        }))

    async def connection_denied_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "connection_denied"
        }))
