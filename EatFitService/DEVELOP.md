# Start enivironment to develop


## Preparations before first start

In EatFitServie/EatFitService copy the key settings file.
```
cp settings_keys.template.py settings_keys.py
```

In `EatFitService/` start docker container:
```
docker-compose up -d
```

Start Shell in container:
```
docker-compose exec api bash
```

Run commands (in docker shell) to migrate DB and collect static files:
```
python manage.py collectstatic --noinput
python manage.py migrate
```

To create a user to log in run this command and enter the information requested:
```
python manage.py createsuperuser
```

## Start Django Server
Make sure docker-compose runs:
```
docker-compose up -d
```

Log in to docker container:
```
docker-compose exec api bash
```

Start the Django server in the docker shell:
```
python manage.py runserver 0.0.0.0:81
```

Now on your local machine you should be able to open the browser at: http://localhost:81/

Make sure to run `python manage.py migrate` whenever you create new DB migrations.

