from kafka import KafkaProducer
import logging

from users_service import settings

logger = logging.getLogger('users_service')


def produce_profile_notification(user_id: int):
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        value_serializer=lambda v: str(v).encode('utf-8')
    )

    message = f"User: {user_id} updated his profile"
    producer.send("profile_notifications", message)
    producer.flush()
    logger.debug(f'Message sent: {message}')
    producer.close()
