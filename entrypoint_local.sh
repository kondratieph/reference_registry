#!/usr/bin/env bash

python manage.py migrate
python manage.py create_admin
python manage.py runserver 0.0.0.0:8000
