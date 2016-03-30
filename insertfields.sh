cat << EOF | docker-compose run web python manage.py shell
from miroutes.models import Country, Area, Spot, Wall, Route, RouteGeometry
from django.core.files import File

c = Country(country_name="TestCountry", country_code=1234)
c.save()

a = Area(area_name="testArea", area_country=c, area_grade_system=0)
a.save()

gKochel = {u'coordinates': [11.344199180603026, 47.632660340454386], u'type': u'Point'}
gKochel2 = {u'coordinates': [11.644199180603026, 47.632660340454386], u'type': u'Point'}

gWiesenwand = {u'coordinates': [11.347973048686981, 47.63621916824778], u'type': u'Point'}
gKeltenwand = {u'coordinates': [11.346226930618286, 47.634681075868414], u'type': u'Point'}

s = Spot(spot_name="testSpot", spot_area=a, geom=gKochel)
s.save()

s2 = Spot(spot_name="testSpot2", spot_area=a, geom=gKochel2)
s2.save()

fname_image = "/code/misc/kochel_seewand_pano.png"

w = Wall(wall_name="Wiesenwand", is_active=True, wall_spot=s, geom=gWiesenwand)
w.save()
w.background_img.save('seewand_pano.png', File(open(fname_image)))

r = Route(route_name="testRoute1", route_grade="5b", route_spot=s)
r.save()

route_geom = { u'coordinates':[ [90, -i] for i in xrange(9,25) ], u'type': u'LineString'}

geom_obj = RouteGeometry(route=r, on_wallview=w.wallview_set.filter(is_dev=False)[0], geom=route_geom)
geom_obj.save()

fname_image = "/code/misc/lost_arrow.png"

w = Wall(wall_name="Keltenwand", is_active=False, wall_spot=s, geom=gKeltenwand)
w.save()
w.background_img.save('lost_arrow.png', File(open(fname_image)))

r = Route(route_name="testRoute1", route_grade="6b", route_spot=s)
r.save()

route_geom = { u'coordinates':[ [90, -i] for i in xrange(9,25) ], u'type': u'LineString'}

geom_obj = RouteGeometry(route=r, on_wallview=w.wallview_set.filter(is_dev=False)[0], geom=route_geom)
geom_obj.save()
EOF
