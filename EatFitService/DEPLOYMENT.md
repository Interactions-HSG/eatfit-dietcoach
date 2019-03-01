# Deployment Guide

## Create log file

Move to directory `/var/log/apache2`

Create log file and grant corrct permissions:

```
touch nutrition-service.log
chmod 777 nutrition-service.log
```

## Update Packages

Move to directory 

```
source env/bin/activate
pip install -r requirements.txt
```

## Apply migrations

`python manage.py migrate`

## Run Tests

`py.test -s -v`

## Restart Apache

`apache2ctl restart`