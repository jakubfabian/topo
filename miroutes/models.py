
from djgeojson.fields import PointField
from djgeojson.fields import LineStringField
from django.db import models
from django.conf import settings

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
            #import pdb; pdb.set_trace()
            print("tiles_file_path does not exist", storage.path(file_path), storage.path(tiles_file_path))
            self.tile_image(storage.path(file_path), storage.path(tiles_file_path))
            return "success"
        except:
            return "error"

    def get_tiles_url(self):
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
            #res = newdim+zoom_levels
            return ' ,'.join( [ str(d) for d in res ] )
        return ''

    def tile_image(self,src,dst):
        try:
            from PIL import Image
            import os
            import numpy as np

            image = Image.open(src)

            tile_width = 256
            dim = image.size
            print(dim)
            
            #newdim = [ int(np.ceil(1.*d/tile_width)*tile_width) for d in dim ]
            newxdim = int(tile_width*2**(np.ceil((np.log(dim[0] / tile_width) / np.log(2)))))
            newydim = int(np.ceil(1.*dim[1]/tile_width)*tile_width)
            newdim = [newxdim, newydim]
            #import ipdb;ipdb.set_trace()

            wpercent = (newxdim/float(image.size[0]))
            hsize = int((float(image.size[1])*float(wpercent)))
            image = image.resize((newxdim, hsize), Image.ANTIALIAS)
            image.save(src)

            image2 = Image.new('RGBA',newdim)
            image2.paste(image,(0,0))
            print( image2.size)

            zoom_levels = np.int( np.ceil( np.log( np.max(newdim) /tile_width)/np.log(2) ))
            print("Image Tiler zoom levels",zoom_levels)
            for z in range(zoom_levels+1):
                dim2 = image2.size
                x2 = 0
                print("zloop",dim2)
                for x in range(0, dim2[0]- 1 , tile_width):
                    y2 = 0
                    for y in range( 0, dim2[1]- 1 , tile_width):
                        paths = [ str(dst), str(int(zoom_levels-z)), str(x2) ]
                        path=''
                        for p in paths:
                            path+=p+u'/'
                            if not os.path.exists(path): os.mkdir(path)

                        tile = image2.crop((x,y, x + tile_width, y + tile_width))
                        fname = u"/".join(paths)+u"/"+str(y2)+u".png"
                        tile.save(fname)
                        print(fname)
                        y2 = y2 + 1
                    x2 = x2 + 1

                image2 = image2.resize((dim2[0]//2, dim2[1]//2), Image.ANTIALIAS)
        except Exception as inst:
            print("Error occured in tile_image",inst)



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

