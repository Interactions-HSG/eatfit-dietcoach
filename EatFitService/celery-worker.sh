#!/usr/bin/env bash

mkdir -p /home/eatfit/eatfitrepo/EatFitService/logs
touch /home/eatfit/eatfitrepo/EatFitService/logs/celery.log


service supervisor start
supervisorctl reread
supervisorctl update
supervisorctl start all

tail -f /home/eatfit/eatfitrepo/EatFitService/logs/celery.log