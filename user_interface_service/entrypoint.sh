#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input
cp -r /app/static/* /static/

gunicorn -c gunicorn_config.py user_interface_service.wsgi:application
