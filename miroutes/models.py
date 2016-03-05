
from djgeojson.fields import PointField
from djgeojson.fields import LineStringField
from django.db import models
from django.conf import settings

from miroutes.image_tiler import tile_image

# Create your models here.
class Country(models.Model):
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=4)
    def __str__(self):
        return self.country_name

class Area(models.Model):
    area_name = models.CharField(max_length=100)
    area_country = models.ForeignKey(Country)
    def __str__(self):
        return self.area_name

class Spot(models.Model):
    spot_name = models.CharField(max_length=100)
    spot_area = models.ForeignKey(Area)
    geom = PointField()
    def __str__(self):
        return self.spot_name


def get_bg_img_upload_path(instance, filename):
    """
    Define default basename for where to put wall background images inside media dir
    """
    import os
    from time import gmtime, strftime
    time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())+'_'+filename
    return os.path.join("wall_pictures",'{}'.format(instance.wall_name),"background",str(time))



class Wall(models.Model):
    wall_name = models.CharField(max_length=100)
    wall_spot = models.ForeignKey(Spot)
    geom = PointField()
    background_img = models.ImageField(blank = True, upload_to=get_bg_img_upload_path)

    def __str__(self):
        return self.wall_name

    @property
    def popupContent(self):
        return "Test"

    def save(self, *args, **kwargs):
        super(Wall, self).save(*args, **kwargs)
        self.create_tiles()

    def create_tiles(self):
        """
        Tiling procedure
        We take the Wall background image, create the tiles and save them in the local path to the media dir
        """
        import os
        from PIL import Image
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
            tile_image(storage.path(file_path), storage.path(tiles_file_path))
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
        import os
        from django.core.files.storage import default_storage as storage
        from PIL import Image
        import numpy as np
            #import pdb; pdb.set_trace()
        if not self.background_img:
            return ""
        file_path = self.background_img.name
        if storage.exists(file_path):
            image = Image.open(storage.path(file_path))
            tile_width = 256
            dim = image.size

            newdim = [ int(np.ceil(1.*d/tile_width)*tile_width) for d in dim ]
            zoom_levels = [ np.int(np.ceil(zl)) for zl in np.log( np.array(newdim)/tile_width)/np.log(2) ]

            res = list(dim)+zoom_levels
            return ' ,'.join( [ str(d) for d in res ] )
        return ''




class Route(models.Model):

    GRADE_CHOICES = (
        ('5', '5b'),
        ('5b', '5b'),
        ('5c', '5c'),
        ('6a', '6a'),
        ('6b', '6b')
    )



    route_name = models.CharField(max_length=100)
    route_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default="5b")
    route_wall = models.ForeignKey(Wall)
    geom = LineStringField()
    def __str__(self):
        return self.route_name

