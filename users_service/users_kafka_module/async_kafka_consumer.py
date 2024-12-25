import logging
import re

from aiokafka import AIOKafkaConsumer
from django.conf import settings

from users_app.mongomodels import Notification
from users_app.services import UserService

logger = logging.getLogger('logger')


def extract_user_id(message):
    logger.debug(message)
    match = re.search(r"User: (\d+)", message)
    logger.debug(match)

    if match:
        user_id_extracted = int(match.group(1))
        return user_id_extracted
    else:
        return None


async def consume_profile_notifications():
    consumer = AIOKafkaConsumer(
        "profile_notifications",
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        group_id="notification_service",
        value_deserializer=lambda x: x.decode('utf-8')
    )
    await consumer.start()
    try:
        async for message in consumer:
            logger.debug(f'Message arrived: {message.value}')
            await send_profile_notification(message.value)
    finally:
        await consumer.stop()


async def send_profile_notification(message: str):
    logger.debug(f'Message arrived to target: {message}')

    user_id = extract_user_id(message)
    logger.debug(f'User id: {user_id}')

    notification = Notification(
        user_id=user_id,
        message=message,
        type='profile_notification',
        status='unread',
    )
    notification.save()
    logger.debug(notification.id)


async def consume_post_notifications():
    consumer = AIOKafkaConsumer(
        "post_notifications",
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        group_id="notification_service",
        value_deserializer=lambda x: x.decode('utf-8')
    )
    await consumer.start()
    try:
        async for message in consumer:
            logger.debug(f'Message arrived: {message.value}')
            await send_post_notification(message.value)
    finally:
        await consumer.stop()


async def send_post_notification(message: str):
    logger.debug(f'Message arrived to target: {message}')
    user_id = extract_user_id(message)
    await UserService.send_post_notifications(user_id, message)
    