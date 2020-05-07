# EatFitService

## Setup for Development Environment

### Requirements

Make sure to have Docker installed on your system. Installation guides can be found [here](https://docs.docker.com/install/).

### First-time build or after changes in source code
`docker-compose up --build -d` 

### Shell access within container
`docker-compose exec api bash`

### Create superuser for django-admin
```
python manage.py createsuperuser
Username (leave blank to use 'root'): adnexo_admin
Email address:
Password: 
Password (again): 
Superuser created successfully.
```

### Running Tests
Once inside the container:
```
source /usr/local/venvs/eatfitenv/bin/activate
pytest -s -v
```

## Create Database Dump
`mysqldump -u root -p NutritionDB > [FILE NAME].sql`

## Upload Images to Azure
`azcopy --source [IMAGE FILE] --dest-key [KEY] --destination https://eatfitmedias.blob.core.windows.net/media/ --recursive`

## Swagger UI
can be found under the url `/static/swagger/`