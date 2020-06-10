FROM python:3.6-stretch
RUN apt-get update
RUN apt-get install -y apt-utils supervisor python3 python3-dev default-libmysqlclient-dev build-essential unixodbc unixodbc-dev apache2 apache2-utils apache2-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/letsencrypt/live/localhost
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/letsencrypt/live/localhost/privkey.pem \
    -out /etc/letsencrypt/live/localhost/fullchain.pem \
    -subj /CN=localhost
WORKDIR "/home/eatfit/eatfitrepo/EatFitService"
ADD . .
ADD ./000-default-le-ssl.conf /etc/apache2/sites-enabled/000-default-le-ssl.conf
ADD ./000-default.conf /etc/apache2/sites-enabled/000-default.conf
ADD ./options-ssl-apache.conf /etc/letsencrypt/options-ssl-apache.conf
ADD ./EatFitService-celery.conf /etc/supervisor/conf.d/EatFitService-celery.conf
RUN pip install virtualenv
RUN mkdir /usr/local/venvs && python -m virtualenv /usr/local/venvs/eatfitenv
RUN . /usr/local/venvs/eatfitenv/bin/activate && \
    pip install -r requirements.txt && \
    wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.6.5.tar.gz && \
    tar xvfz 4.6.5.tar.gz && \
    cd mod_wsgi-4.6.5 && \
    ./configure && \
    make && \
    make install && \
    make clean
ADD ./modules.load /etc/apache2/mods-enabled/modules.load
RUN chown -R www-data:www-data /home/eatfit/eatfitrepo/EatFitService
RUN chmod 775 -R /home/eatfit/eatfitrepo/EatFitService
RUN touch /var/log/nutrition-service.log
RUN chmod 777 /var/log/nutrition-service.log
RUN mkdir -p ./cache
RUN chmod 777 ./cache
RUN pip install -r requirements.txt