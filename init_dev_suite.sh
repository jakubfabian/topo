#!/usr/bin/env bash
#
# Script to setup inital project and add some first stuff into database to get going
# includes 
#   docker image bulding
#   creation of superuser
#   insert test wall with 2 routes

#setup docker images and run them
#the command line parameters are forwarded to build
docker-compose build $@
docker-compose start db 
docker-compose start web 

# then use docker-compose up to restart all containers and run them in background
docker-compose up -d
sleep 2

# make migrations and migrate to setup db
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
sleep 3

# Create root admin user
echo "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'myemail@example.com', 'root')" | docker-compose run web python manage.py shell












