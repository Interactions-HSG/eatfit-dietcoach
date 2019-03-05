# Deployment Guide

## Create file holding keys from settings_keys.template.py

```
cp settings_keys.template.py settings_keys.py
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