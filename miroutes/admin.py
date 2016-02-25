from leaflet.admin import LeafletGeoAdmin
from djgeojson.fields import PointField
from django.contrib import admin

from miroutes.models import Country
from miroutes.models import Area
from miroutes.models import Spot
from miroutes.models import Wall
from miroutes.models import Route



# Register your models here.


class AreaAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['area_name']}),
        ('Country:', {'fields': ['area_country']})
        ]
    list_filter = ['area_country']

class SpotAdmin(admin.ModelAdmin):

    list_filter = ['spot_area']

class CountryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['country_name']}),
        ('Additional Info:', {'fields': ['country_code']})
        ]


class WallAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['wall_name']}),
        ('Area:', {'fields': ['wall_spot']})
        ]
    list_filter = ['wall_spot']

class RouteAdmin(admin.ModelAdmin):
    list_filter = ['route_wall']





admin.site.register(Country, CountryAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Spot, LeafletGeoAdmin)
admin.site.register(Wall, LeafletGeoAdmin)
admin.site.register(Route, LeafletGeoAdmin)
