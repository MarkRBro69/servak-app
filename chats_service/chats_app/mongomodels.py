from mongoengine import Document, StringField, IntField, DateTimeField
import datetime


class Notification(Document):
    user_id = IntField(required=True)
    message = StringField(required=True)
    type = StringField(required=True)
    status = StringField(default='unread')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': ['user_id', 'type', 'status'],
        'ordering': ['-created_at'],
    }
