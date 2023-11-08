#!/bin/bash

python3 manage.py collectstatic --no-input
python3 manage.py migrate
#python3 manage.py runserver
uwsgi --strict --ini /uwsgi.ini