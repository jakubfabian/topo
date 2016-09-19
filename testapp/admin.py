from leaflet.admin import LeafletGeoAdmin
from djgeojson.fields import PointField
from django.contrib import admin

from testapp.models import Country
from testapp.models import Area
from testapp.models import Spot
from testapp.models import Wall
from testapp.models import Route



# Register your models here.


class AreaAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Country:', {'fields': ['country']})
        ]
    list_filter = ['country']

class SpotAdmin(admin.ModelAdmin):

    list_filter = ['area']

class CountryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Additional Info:', {'fields': ['country_code']})
        ]


class WallAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Area:', {'fields': ['spot']})
        ]
    list_filter = ['spot']

class RouteAdmin(admin.ModelAdmin):
    list_filter = ['route_wall']





admin.site.register(Country, CountryAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Spot, LeafletGeoAdmin)
admin.site.register(Wall, LeafletGeoAdmin)
admin.site.register(Route, LeafletGeoAdmin)
