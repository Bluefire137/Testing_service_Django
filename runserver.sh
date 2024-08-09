#!/bin/bash

python manage.py migrate --noinput
python create_superuser.py
python manage.py runserver 0.0.0.0:8000
