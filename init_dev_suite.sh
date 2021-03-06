#!/usr/bin/env bash
#
# Script to setup inital project and add some first stuff into database to get going
# includes 
#   docker image bulding
#   creation of superuser
#   insert test wall with 2 routes

# then use docker-compose up to restart all containers and run them in background
docker-compose up -d
sleep 5

# make migrations and migrate to setup db
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py makemigrations miroutes
docker-compose run web python manage.py makemigrations users
docker-compose run web python manage.py migrate
sleep 5

# Create root admin user
echo "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'myemail@example.com', 'root')" | docker-compose run web python manage.py shell
docker-compose restart
sleep 5

sh insertfields.sh

docker-compose ps

# In order to overwrite the django-star_rating images, we need to call collectstatic at least once
docker-compose run web python manage.py collectstatic
