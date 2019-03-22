#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate
service supervisor start
supervisorctl reread
supervisorctl update
supervisorctl start all