# Deployment Guide

## Create log file

Move to directory `/var/log/`

Create log file and grant corrct permissions:

```
touch nutrition-service.log
chmod 777 nutrition-service.log
```

## Create file holding keys from settings_keys.template.py

```
SECRET_KEY = 'Secret'
REEBATE_USERNAME = 'Secret'
REEBATE_PASSWORD = 'Secret'
TRUSTBOX_USERNAME = 'Secret'
TRUSTBOX_PASSWORD = 'Secret'
EMAIL_HOST_USER = 'Secret'
EMAIL_HOST_PASSWORD = 'Secret'
AZURE_STORAGE_KEY = 'Secret'

```

## Update Packages

Move to directory 

```
source env/bin/activate
pip install -r requirements.txt
```

## Apply migrations

`python manage.py migrate`

## Collect static files

`python manage.py collectstatic`

## Run Tests

`py.test -s -v`

## Restart Apache

`apache2ctl restart`