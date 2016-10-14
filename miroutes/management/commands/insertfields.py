from django.core.management import BaseCommand

from miroutes.models import Spot, Wall, Route, RouteGeometry
from django.core.files import File


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Creates initial database objects as sample content"

    # A command must define handle()
    def handle(self, *args, **options):
        self.stdout.write("Creating initial database objects")

        gKochel = {u'coordinates': [11.344199180603026, 47.632660340454386], u'type': u'Point'}
        gPampa = {u'coordinates': [11.644199180603026, 47.632660340454386], u'type': u'Point'}

        gWiesenwand = {u'coordinates': [11.347973048686981, 47.63621916824778], u'type': u'Point'}
        gKeltenwand = {u'coordinates': [11.346226930618286, 47.634681075868414], u'type': u'Point'}

        s = Spot(name="Kochel", geom=gKochel)
        s.save()

        s2 = Spot(name="Pampa", geom=gPampa)
        s2.save()

        fname_image = "/code/misc/kochel_wiesenwand.png"

        w = Wall(name="Wiesenwand", is_active=True, spot=s, geom=gWiesenwand)
        w.save()
        w.background_img.save('seewand_pano.png', File(open(fname_image)))

        for j in range(0, 5):
            r = Route(name="testRoute" + str(j), grade="201", spot=s)
            r.save()

            route_geom = {u'coordinates': [[90 + j * 3, -i] for i in xrange(9, 25)], u'type': u'LineString'}

            geom_obj = RouteGeometry(route=r, on_wallview=w.dev_view, geom=route_geom)
            geom_obj.save()

        w.publish_dev_view()

        fname_image = "/code/misc/lost_arrow.png"

        w = Wall(name="Keltenwand", is_active=False, spot=s, geom=gKeltenwand)
        w.save()
        w.background_img.save('lost_arrow.png', File(open(fname_image)))

        r = Route(name="testRoute1", grade=101, spot=s2)
        r.save()

        route_geom = {u'coordinates': [[90, -i] for i in xrange(9, 25)], u'type': u'LineString'}

        geom_obj = RouteGeometry(route=r, on_wallview=w.wallview_set.filter(is_dev=False)[0], geom=route_geom)
        geom_obj.save()
