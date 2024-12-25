import logging

from aiokafka import AIOKafkaConsumer
from django.conf import settings

logger = logging.getLogger('logger')


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
            await send_notification(message.value)
    finally:
        await consumer.stop()


async def send_notification(message: str):
    logger.debug(f'Message arrived to target: {message}')
