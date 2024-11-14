#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input
cp -r /app/static/* /static/

exec gunicorn -c gunicorn_config.py users_service.wsgi:application