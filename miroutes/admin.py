from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from miroutes.models import Route
from miroutes.models import RouteGeometry
from miroutes.models import Spot
from miroutes.models import Wall


# Register your models here.

class SpotAdmin(admin.ModelAdmin):
    pass

class WallAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name','spot']}),
        ]
    list_filter = ['spot']

class RouteAdmin(admin.ModelAdmin):
    list_filter = ['route_wall']

admin.site.register(Spot, LeafletGeoAdmin)
admin.site.register(Wall, LeafletGeoAdmin)
admin.site.register(Route, LeafletGeoAdmin)
admin.site.register(RouteGeometry, LeafletGeoAdmin)
