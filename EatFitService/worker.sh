#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

apache2ctl stop
apache2ctl -DFOREGROUND