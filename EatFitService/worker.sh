#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate

apache2ctl -DFOREGROUND