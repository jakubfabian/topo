
def tile_image(src, dst, tile_width=256):
    """
    Tile an image for use in leafletjs
    Files will be save at dst/zoomlvl/x_direction/y_direction.png
    """
    try:
        from PIL import Image, ExifTags
        import os
        import numpy as np
        #import ipdb;ipdb.set_trace()

        image = Image.open(src)

        # If we are dealing with a jpeg we read the exif data to see if it should be
        # rotated
        if os.path.splitext(src)[1] == ".jpeg":
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                    exif = dict(image._getexif().items())

                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)

            except:
                print "Could not read EXIF data from image {}.".format(src)


        width, height = image.size
        print(width, height)

        if width >= height:
            # Compute new dimensions being a power of 2 in width while maintaining aspect ratio
            newwidth = np.int(2**np.ceil(np.log2(width)))
            wpercent = (newwidth/float(width))
            newheight = np.int(height*wpercent)
        else:
            # Compute new dimensions being a power of 2 in height while maintaining aspect ratio
            newheight = np.int(2**np.ceil(np.log2(height)))
            hpercent = (newheight/float(height))
            newwidth = np.int(width*hpercent)
            
        image = image.resize((newwidth, newheight), Image.ANTIALIAS)

        # Overwrite image with enlarged version
        image.save(src)

        # Convert Image to RGBA to use alpha channel to get transparent edge areas (where no image is defined)
        image2 = Image.new('RGBA', image.size)
        image2.paste(image,(0,0)) 
        print( image2.size)

        # Max number of zoom levels:
        zoom_levels = np.int( np.ceil( np.log2( np.max(image.size) /tile_width) ))
        print("Image Tiler zoom levels",zoom_levels)

        # Iterate over zoom levels and for each line of tiles in the image, crop tiles out of the temporary image and save it to disk
        for z in range(zoom_levels+1):
            dim2 = image2.size
            x2 = 0
            print("zloop:",z,':: current image size:',dim2)
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
