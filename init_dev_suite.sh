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

# make migrations and migrate to setup db
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate

# Create root admin user
echo "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'myemail@example.com', 'root')" | docker-compose run web python manage.py shell

# Fill in some stuff into Database
cat << EOF | docker-compose run web python manage.py shell
from miroutes.models import Country, Area, Spot, Wall, Route, RouteGeometry
from django.core.files import File

c = Country(country_name="TestCountry", country_code=1234)
c.save()

a = Area(area_name="testArea", area_country=c)
a.save()

gKochel = {u'coordinates': [11.344199180603026, 47.632660340454386], u'type': u'Point'}
gWiesenwand = {u'coordinates': [11.347973048686981, 47.63621916824778], u'type': u'Point'}
gKeltenwand = {u'coordinates': [11.346226930618286, 47.634681075868414], u'type': u'Point'}

s = Spot(spot_name="testSpot", spot_area=a, geom=gKochel)
s.save()

fname_image = "/code/misc/kochel_seewand_pano.png"
w = Wall(wall_name="Wiesenwand", is_active=True, wall_spot=s, geom=gWiesenwand)
w.background_img.save('fname_from_function.png', File(open(fname_image)))

r = Route(route_name="testRoute1", route_grade="5b", route_spot=s)
r.save()

route_geom = { u'coordinates':[ [90, -i] for i in xrange(9,25) ], u'type': u'LineString'}

geom_obj = RouteGeometry(route=r, on_wall=w, geom=route_geom)
geom_obj.save()

fname_image = "/code/misc/lost_arrow.png"
w = Wall(wall_name="Keltenwand", wall_spot=s, geom=gKeltenwand)
w.background_img.save('fname_from_function.png', File(open(fname_image)))

r = Route(route_name="testRoute1", route_grade="6b", route_spot=s)
r.save()

route_geom = { u'coordinates':[ [90, -i] for i in xrange(9,25) ], u'type': u'LineString'}

geom_obj = RouteGeometry(route=r, on_wall=w, geom=route_geom)
geom_obj.save()
EOF

