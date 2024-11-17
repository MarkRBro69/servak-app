import json

from django.conf import settings
from kafka import KafkaProducer


def produce_chat_notification(user_id: int, user_to_invite: int, room_id: str):
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    message = {
        'user_id': user_id,
        'user_to_invite': user_to_invite,
        'room_id': room_id,
    }
    producer.send("invite_notifications", message)
    producer.flush()
    producer.close()
