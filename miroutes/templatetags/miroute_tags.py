from django import template
from ast import literal_eval

register = template.Library()

@register.filter(name='linestringgeomfilter')
def get_linestringgeom(value):
    """Filter GEOJson linestrings to generate a coordinate array which can be
    used to make polylines.

    Throws:
        AssertionError, KeyError
    """
    assert type(value.geom) == unicode, 'Not a valid unicode linestring %s' % str(value.geom)
    geomdict = literal_eval(value.geom)
    assert type(geomdict) == dict, 'Can not convert %s to a dict.' % str(geomdict)

    # we reverse [x=lng, y=lat] to fit to [lat, lng]
    return [[coord[1], coord[0]] for coord in geomdict['coordinates']]        
