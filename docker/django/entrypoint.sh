#!/bin/bash

echo " >>>> Collecting static"
python3 manage.py collectstatic --no-input

echo " >>>> Running migrations"
python3 manage.py migrate

echo " >>>> Running server"
uwsgi --strict --ini uwsgi.ini