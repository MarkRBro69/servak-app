from kafka import KafkaProducer
import logging

from posts_service import settings

logger = logging.getLogger('posts_service')


def produce_post_notification(user_id: int, post_id: int):
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        value_serializer=lambda v: str(v).encode('utf-8')
    )

    message = f"User: {user_id} created post: {post_id}"
    producer.send("post_notifications", message)
    producer.flush()
    logger.debug(f'Message sent: {message}')
    producer.close()
