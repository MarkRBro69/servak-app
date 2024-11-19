#!/bin/sh

python manage.py collectstatic --no-input
cp -r /app/static/* /static/

exec uvicorn chats_service.asgi:application --host 0.0.0.0 --port 8004 --workers 4