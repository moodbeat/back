#!/bin/sh

pip3 install -r /app/requirements.txt --no-cache-dir
python manage.py migrate --noinput
python manage.py collectstatic --noinput
daphne -p 8000 conf.asgi:application
exec "$@"
