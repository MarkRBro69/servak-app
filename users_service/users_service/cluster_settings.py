LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'logger': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

USERS_SERVICE_URL = 'users-service.servak-app.svc.cluster.local'
POSTS_SERVICE_URL = 'posts-service.servak-app.svc.cluster.local'
CHATS_SERVICE_URL = 'chats-service.servak-app.svc.cluster.local'

KAFKA_BROKER_URL = "kafka-0.kafka.servak-app.svc.cluster.local:9092"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis.servak-app.svc.cluster.local:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'servakdb',
        'USER': 'postgres',
        'PASSWORD': 'Qecz1357',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

MONGO_URI = 'mongodb://mongodb.servak-app.svc.cluster.local:27017/notification_db'
MONGO_NAME = 'notification_db'

ALLOWED_HOSTS = [
    '127.0.0.1',
    '127.0.0.2',
    'localhost',
    'users_service',
    'posts_service',
    'chats_service',
    'users-service.servak-app.svc.cluster.local',
    'chats-service.servak-app.svc.cluster.local',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://users_service',
    'http://posts_service',
    'http://posts-service.servak-app.svc.cluster.local',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://users_service',
    'http://posts_service',
    'http://posts-service.servak-app.svc.cluster.local',
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis.servak-app.svc.cluster.local", 6379)],
            "DB": 1,
        },
    },
}
