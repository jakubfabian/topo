
from djgeojson.fields import PointField
from djgeojson.fields import LineStringField
from django.db import models


# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=4)
    def __str__(self):
        return self.name

class Area(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country)
    def __str__(self):
        return self.name

class Spot(models.Model):
    name = models.CharField(max_length=100)
    area = models.ForeignKey(Area)
    geom = PointField()
    def __str__(self):
        return self.name


def get_bg_img_upload_path(instance, filename):
    import os
    from time import gmtime, strftime
    time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())+'_'+filename
    return os.path.join("wall_pictures",'{}'.format(instance.name),"background",str(time))



class Wall(models.Model):
    name = models.CharField(max_length=100)
    spot = models.ForeignKey(Spot)
    geom = PointField()
    background_img = models.ImageField(blank = True,upload_to=get_bg_img_upload_path)

    def __str__(self):
        return self.name

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
            print("tiles_file_path does not exist",storage.path(file_path),storage.path(tiles_file_path))
            self.tile_image(storage.path(file_path),storage.path(tiles_file_path))
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
        if storage.exists(tiles_file_path):
            return storage.url(tiles_file_path)
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

            newdim = [ int(np.ceil(1.*d/tile_width)*tile_width) for d in dim ]

            wpercent = (newdim[0]/float(image.size[0]))
            hsize = int((float(image.size[1])*float(wpercent)))
            image = image.resize((newdim[0],hsize), Image.ANTIALIAS)
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
                #import ipdb; ipdb.set_trace()
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



    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default="5b")
    route_wall = models.ForeignKey(Wall)
    geom = LineStringField()
    def __str__(self):
        return self.name

