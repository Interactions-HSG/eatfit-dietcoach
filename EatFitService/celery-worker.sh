#!/usr/bin/env bash

service supervisor start
supervisorctl reread
supervisorctl update
supervisorctl start all