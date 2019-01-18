# EatFitService

## Setup for Development Environment

### Requirements

Make sure to have Docker installed on your system. Installation guides can be found [here](https://docs.docker.com/install/).

### Dockerfile

The main Docker file for building the API is `Dockerfile.dev` and contains the following steps:

1. Install Python 2.7.15 from jessie (Debian)
2. Build minimal system for serving the application
	- Python development tools
	- MySQL database connection tools
	- Apache2 server tools
	- Letsencrypt for SSL-certificates
3. Create SSL-certificates
4. Copy project and apache2 configuration files to Debian image
5. Create a Python virtual environment and install dependencies
6. Grant the Apache2 user (www-data on Debian) following permissions for project file systems:
	- User: read / write / execute (7)
	- Group: read / write / execute (7)
	- World: read / execute (5)
7. Run worker shell script which collects the project's static files, runs database migrations and runs the Apache2 server.

The code:

```
FROM python:2.7-jessie
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y apt-utils python-dev libmysqlclient-dev build-essential unixodbc unixodbc-dev apache2 apache2-utils libapache2-mod-wsgi letsencrypt -t jessie-backports
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/letsencrypt/live/localhost
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/letsencrypt/live/localhost/privkey.pem \
    -out /etc/letsencrypt/live/localhost/fullchain.pem \
    -subj /CN=localhost
WORKDIR "/home/eatfit/eatfitrepo/EatFitService"
COPY . .
ADD ./000-default-le-ssl.conf /etc/apache2/sites-enabled/000-default-le-ssl.conf
ADD ./000-default.conf /etc/apache2/sites-enabled/000-default.conf
ADD ./options-ssl-apache.conf /etc/letsencrypt/options-ssl-apache.conf
ADD ./modules.load /etc/apache2/mods-enabled/modules.load
RUN virtualenv env
RUN . env/bin/activate
RUN pip install -r requirements.txt
RUN chown -R www-data:www-data /home/eatfit/eatfitrepo/EatFitService
RUN chmod 775 -R /home/eatfit/eatfitrepo/EatFitService
CMD sh worker.sh
```
### Docker Compose Configuration

The composition file for all Docker containers is `docker-compose.yml`:

```
version: '3'
services:
  mysql:
    image: 'mysql:5.7.24'
    environment:
      - MYSQL_USER=root
      - MYSQL_ROOT_PASSWORD=UmwyB9HTKVA2Gyt
      - MYSQL_DATABASE=NutritionDB
      - MYSQL_ROOT_HOST=%
  api:
    build:
      dockerfile: Dockerfile.dev
      context: .
    ports:
      - 80:80
      - 443:443
    depends_on:
      - mysql
```

### Executing the Application

To run the Docker containers use one of the following commands

```
# First-time build or after changes in source code
docker-compose up --build

# Running without build
docker-compose up
```

### Django Superuser and Loading Data into the Database

After the container has been built and is running you can access the command line (`sh`) inside the container:

```
# For a given IMAGE find its corresponding CONTAINER ID
docker ps
docker exec -it <CONTAINER ID> sh
```
Create the Django superuser to access the admin panel:
 
```
./manage.py createsuperuser
Username (leave blank to use 'root'): adnexo_admin
Email address:
Password: 
Password (again): 
Superuser created successfully.
```

There is a JSON fixture called nutritiondb.json which can be used to load data into the database. The command for doing so is:

```
./manage.py loaddata nutritiondb.json --exclude=auth
```

### Obtaining a New Data Dump from the Production Database

Log into the production server and use django to creata a JSON fixture from the database:

```
ssh eatfit@eatfit.northeurope.cloudapp.azure.com
Enter Password:
cd /home/eatfit/eatfitrepo/EatFitService
source env/bin/activate
python manage.py dumpdata --natural-primary --natural-foreign --indent=4 --exclude=sessions --exclude=auth --exclude=authtoken --exclude=admin --exclude=contenttypes > nutritiondb.json
```

Copy the file inside the shell of your local machine as follows:

```
scp eatfit@eatfit.northeurope.cloudapp.azure.com:/home/eatfit/eatfitrepo/EatFitService/nutritiondb.json /path/to/EatFitService/nutritiondb.json
```