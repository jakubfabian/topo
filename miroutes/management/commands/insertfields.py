import random

from django.core.management import BaseCommand

from miroutes.models import Spot, Wall, Route, RouteGeometry
from django.core.files import File


def create_wiesenwands():

    for z in range(1, 10):

        spot_x = 11.34 + random.random()
        spot_y = 47.63 + random.random()
        spot_coord = {u'coordinates': [spot_x, spot_y], u'type': u'Point'}

        s = Spot(name="testSpot" + str(z), geom=spot_coord)
        s.save()

        wiesenwand_coords = {u'coordinates': [spot_x + 0.01, spot_y + 0.01], u'type': u'Point'}
        fname_image = "/code/misc/kochel_seewand_pano.png"

        w = Wall(name="Wiesenwand", is_active=True, spot=s, geom=wiesenwand_coords)
        w.save()
        w.background_img.save('seewand_pano.png', File(open(fname_image)))

        for j in range(0, 30):
            r = Route(name="testRoute" + str(j), grade="5b", spot=s)
            r.save()

            route_geom = {u'coordinates': [[90 + j * 3, -i] for i in xrange(9, 25)], u'type': u'LineString'}

            geom_obj = RouteGeometry(route=r, on_wallview=w.dev_view, geom=route_geom)
            geom_obj.save()

        w.publish_dev_view()

def create_keltenwands():

    for z in range(1, 10):

        spot_x = 11.34 + random.random()
        spot_y = 47.63 + random.random()
        spot_coord = {u'coordinates': [spot_x, spot_y], u'type': u'Point'}

        s = Spot(name="testSpot" + str(z), geom=spot_coord)
        s.save()

        wiesenwand_coords = {u'coordinates': [spot_x + 0.01, spot_y + 0.01], u'type': u'Point'}
        fname_image = "/code/misc/lost_arrow.png"

        w = Wall(name="Keltenwand", is_active=True, spot=s, geom=wiesenwand_coords)
        w.save()
        w.background_img.save('lost_arrow.png', File(open(fname_image)))

        for j in range(0, 30):
            r = Route(name="testRoute" + str(j), grade="5b", spot=s)
            r.save()

            route_geom = {u'coordinates': [[90 + j * 3, -i] for i in xrange(9, 25)], u'type': u'LineString'}

            geom_obj = RouteGeometry(route=r, on_wallview=w.dev_view, geom=route_geom)
            geom_obj.save()

        w.publish_dev_view()

# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Creates initial database objects as sample content"

    # A command must define handle()
    def handle(self, *args, **options):
        self.stdout.write("Creating initial database objects")

        create_wiesenwands()
        create_keltenwands()