from datetime import date
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from djgeojson.fields import LineStringField
from djgeojson.fields import PointField

from miroutes.tasks import tile_image

from itertools import product

RATING_CHOICES = (
    (1, 'poor'),
    (2, 'ok'),
    (3, 'not bad'),
    (4, 'good'),
    (5, 'excellent'))

GRADE_SYSTEMS = (
    (0, 'France'),
    (1, 'UIAA'),
    (2, 'UK'),
    (3, 'Sierra'))

GRADE_CHOICES = [
       (001, '4b+'),
       (002, '4c-'),
       (003, '4c'),
       (004, '4c+'),
       (005, '5a-'),
       (201, 'S, 4a'),
       (202, 'HS, 4b'),
       (203, 'VS, 4c'),
       (204, 'HVS, 5a'),
       (205, 'E1, 5b'),
       (301, '5.4'),
       (302, '5.5'),
       (303, '5.6'),
       (304, '5.7'),
       (305, '5.8')]

# UIAA system entries:
GRADE_CHOICES += [ (100 + x,str(a)+b ) for x,(a,b) in enumerate( list(product(range(2,12), ['-','','+'])))]

class Spot(models.Model):
    """A spot denotes a region with multiple associated walls.

    The walls within a spot should have a common approach.

    Example:
        Schoenhofen is a spot.
        Eisenbahnerwand is a wall.
    """

    DURATION_CHOICES = (
        (timedelta(minutes=15), '15 minutes or less'),
        (timedelta(minutes=30), '30 minutes'),
        (timedelta(hours=1), '1 hour'),
        (timedelta(hours=2), '2 hours'),
        (timedelta(hours=3), 'more than 3 hours'))
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    geom = PointField()
    parking_description = models.TextField(blank=True, null=True)
    parking_geom = PointField(blank=True, null=True)
    approach = models.TextField(blank=True, null=True)
    approach_time = models.DurationField(
        choices=DURATION_CHOICES,
        default=timedelta(minutes=15))
    grade_system = models.IntegerField(default=0, choices=GRADE_SYSTEMS)


    def __str__(self):
        return self.name


def get_bg_img_upload_path(wallimage, filename):
    """
    Define default basename for where to put wall background images inside media dir
    Args:
      filename: Filename of image
    """
    import os
    from time import gmtime, strftime
    time = strftime("%Y-%m-%d-%H-%M-%S", gmtime()) + '_' + filename
    return os.path.join("wall_pictures", "background", str(time))


class ActiveWallViewManager(models.Manager):
    """
    This manager filters all currently active views excluding the dev views.
    """

    def get_queryset(self):
        return super(ActiveWallViewManager, self).get_queryset().filter(wall__is_active=True).filter(is_dev=False)


class WallView(models.Model):
    """
    A wallview hosts meta information that can be changed/improved
    within the lifecycle of a wall.
    It is related to a route through a RouteGeometry object.
    Currently, we statically create two views for each wall,
    one view that is used for publication and one that is used
    for further editing (development).

    Note:
        The many-to-many relation to the routes on the wallview is defined
        on the side of the routes.
    
    Attributes:
        is_dev (boolean): Flags the development version of the wall.
        wall (Wall): The wall object the view is bound to.
        morning_sun, midday_sun, afternoon_sun (BooleanField): 
            Is the sun shining in the morning/midday/afternoon?
        children_friendly (IntegerField): A children-friendly rating (5 choices).
        bolt_quality (IntegerField): A choice field with a bolt quality rating (5 choices).
        wall_height (IntegerField): The approximate height of the wall in meters.
        DIRECTIONS (tuple): The choices for 8 possible orientations of the wall.

        objects (models.Manager): The generic manager of the model.
        active_objects (ActiveWallViewManager): 
            A manager that filters the wallviews which are associated with
            active walls. The development views are excluded.
    """

    wall = models.ForeignKey('Wall')
    is_dev = models.BooleanField(default=False)

    morning_sun = models.NullBooleanField(blank=True, null=True)
    midday_sun = models.NullBooleanField(blank=True, null=True)
    afternoon_sun = models.NullBooleanField(blank=True, null=True)

    children_friendly = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)
    bolt_quality = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)
    wall_height = models.IntegerField(blank=True, null=True)

    objects = models.Manager()
    active_objects = ActiveWallViewManager()


class ActiveWallManager(models.Manager):
    """
    The active wall manager is used to access the active walls.
    """

    def get_queryset(self):
        return super(ActiveWallManager, self).get_queryset().filter(is_active=True)


class Wall(models.Model):
    """
    Hosts basic informations on a wall. The informations that are put
    in the wall model are considered static, i.e., 
    they are not updated by users.
    
    Attributes:
        is_active (Boolean): Flags active (visible) walls.
        spot (Spot): The spot the wall is associated to.
        name (str): Human readable string describing the wall.
        background_img (ImageField): Hosts the image associated with the wall.
        geom (djgeojson.fields.PointField): JSON of the location of the wall on the map.
        objects (Manager): The generic model manager.
        active_objects (ActiveWallManager): Filters for walls with is_active=True.

    Properties:
        dev_view (WallView): Accesses the WallView with is_dev=True.
        pub_view (WallView): Accesses the WallView with is_dev=False.
    """
    name = models.CharField(max_length=100)
    spot = models.ForeignKey(Spot)
    geom = PointField()
    is_active = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveWallManager()

    background_img = models.ImageField(blank=True, upload_to=get_bg_img_upload_path)

    @property
    def dev_view(self):
        return self.wallview_set.filter(is_dev=True)[0]

    @property
    def pub_view(self):
        return self.wallview_set.filter(is_dev=False)[0]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        update_img = False
        super(Wall, self).save(*args, **kwargs)
        if not self.wallview_set.all():
            dev_view = WallView(wall=self, is_dev=True)
            dev_view.save()
            pub_view = WallView(wall=self, is_dev=False)
            pub_view.save()
	    self.save(*args, **kwargs)

    def create_tiles(self):
        """
        Tiling procedure
        We take the Wall background image, create the tiles and save them in the local path to the media dir
        """
        import os
        from django.core.files.storage import default_storage as storage
        if not self.background_img:
            print ("No background image to create tiles for")
            return ""
        file_path = self.background_img.name
        filename_base, filename_ext = os.path.splitext(file_path)
        tiles_file_path = u"%s_tiles" % filename_base
        if storage.exists(tiles_file_path):
            print("tiles_file_path exists")
            return "exists"
        try:
            print("tiles_file_path does not exist", storage.path(file_path), storage.path(tiles_file_path))
            tile_image.delay(storage.path(file_path), storage.path(tiles_file_path))
            return "success"
        except:
            return "error"

    def get_tiles_url(self):
        """
        Return the web adress to the directory containing the tile dir structure
        """
        import os
        from django.core.files.storage import default_storage as storage
        if not self.background_img:
            return ""
        file_path = self.background_img.name
        filename_base, filename_ext = os.path.splitext(file_path)
        tiles_file_path = u"%s_tiles" % filename_base
        print "background_img url: {}".format(self.background_img.url)
        if storage.exists(tiles_file_path):
            return storage.url(tiles_file_path)
        else:
            print "No tiles found for {}".format(filename_base)
            return ""

    def get_bg_img_size(self):
        """
        Return the size of the original background image and the number of zoom levels in x and direction
        @TODO: is this what we really want -- shouldnt it be the image size of the zoom lvl 0 tile?
        """
        from django.core.files.storage import default_storage as storage
        from PIL import Image
        import numpy as np
        # import pdb; pdb.set_trace()
        if not self.background_img:
            return ""
        file_path = self.background_img.name
        if storage.exists(file_path):
            image = Image.open(storage.path(file_path))
            tile_width = 256
            dim = image.size

            newdim = [int(np.ceil(1. * d / tile_width) * tile_width) for d in dim]
            zoom_levels = [np.int(np.ceil(zl)) for zl in np.log(np.array(newdim) / tile_width) / np.log(2)]

            res = list(dim) + zoom_levels
            return ' ,'.join([str(d) for d in res])
        return ''

    def publish_dev_view(self):
        """
        Deletes the current pub_view and copies the dev_view over the pub_view
        """
        # delete the old pub_view
        self.pub_view.delete()

        newpubview = self.dev_view

        # copy the devview
        newpubview.pk = None
        # and make it the new pub_view
        newpubview.is_dev = False
        newpubview.save()

        # Now we still have to update the RouteGeometries on the
        # new pub_view
        for routegeom in self.dev_view.routegeometry_set.all():
            new_routegeom = RouteGeometry(route=routegeom.route,
                                          on_wallview=self.pub_view,
                                          geom=routegeom.geom)
            new_routegeom.save()

    def reset_dev_view(self):
        """
        Deletes the current dev_view and copies the pub_view over the dev_view.
        """
        # delete the old dev_view
        self.dev_view.delete()

        pubview = self.pub_view

        # copy the pub_view
        pubview.pk = None
        # and make it the new dev_view
        pubview.is_dev = True
        pubview.save()

        # Now we still have to update the RouteGeometries on the
        # new dev_view
        for routegeom in self.pub_view.routegeometry_set.all():
            new_routegeom = RouteGeometry(route=routegeom.route,
                                          on_wallview=self.dev_view,
                                          geom=routegeom.geom)
            new_routegeom.save()


class Route(models.Model):
    """
    Meta data for a route object. Similar to the wall object uniquely refers
    to an existing route, with multiple route geometries on different wall views.

    Attributes:
        spot: The spot the route can be found on.
        walls: The walls the route can be found on.
            This list is generated from the RouteGeometry objects.
        name: The name of the route.
        grade: The grade of the route.
        rating: The (average) rating of the route.
            This should be chosen in agreement with the grading system of the area.
        length: The approximate length of the route in meters.
        number_of_bolts: The number of bolts and thus the number of
            quickdraws that are required to climb the route.
        security_rating: How secure is climbing the route? (1-5)
        description: Comments and caveats on the route.
        
    """

    # Every route is located at a climbing spot
    spot = models.ForeignKey(Spot, default=None)
    # The relation to one or many walls is via the geometry of the route
    walls = models.ManyToManyField(WallView, through='RouteGeometry')
    climbers = models.ManyToManyField(User, through='Ascent')

    name = models.CharField(max_length=100)

    grade = models.IntegerField(choices=GRADE_CHOICES)

    rating = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)

    length = models.IntegerField(blank=True, null=True)

    number_of_bolts = models.IntegerField(blank=True, null=True)
    security_rating = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class RouteGeometry(models.Model):
    """
    The geometry of a route that is specific to a wall.
    """
    on_wallview = models.ForeignKey(WallView)
    route = models.ForeignKey(Route)
    geom = LineStringField()


class Ascent(models.Model):
    """
    Relates a user (climber) to a route "through" the details of
    a climbing attempt.
    """
    STYLE_CHOICES = (('flash', 'flash'),
                     ('on-sight', 'on-sight'),
                     ('red point', 'red point'),
                     ('top rope', 'top rope'))

    climber = models.ForeignKey(User)
    route = models.ForeignKey(Route)
    date = models.DateField(default=date.today)

    style = models.CharField(max_length=10, blank=True, null=True, choices=STYLE_CHOICES)
    rating = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
