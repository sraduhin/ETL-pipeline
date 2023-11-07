#!/bin/bash

echo "Collect static files"
python3 manage.py collectstatic --no-input

echo "Run migrations"
python3 manage.py migrate --no-input

echo "Starting server"
uwsgi --strict --ini uwsgi.ini
