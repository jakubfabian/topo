import ipdb

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from miroutes.models import Country
from miroutes.models import Area
from miroutes.models import Spot
from miroutes.models import Wall
from miroutes.models import Route




def index(request):
    country_listing = Country.objects.order_by('country_name')[:5]
    area_listing = Area.objects.order_by('area_name')
    spot_listing = Spot.objects.order_by('spot_name')
    wall_listing = Wall.objects.order_by('wall_name')
    route_listing = Route.objects.order_by('route_name')
    context = {'country_listing': country_listing, 'area_listing': area_listing, 'spot_listing': spot_listing, 'wall_listing': wall_listing, 'route_listing': route_listing}
    return render(request, 'miroutes/index.html', context)


def country_detail(request, country_id):
    p = get_object_or_404(Country, pk=country_id)
    arealist = p.area_set.all()
    spotlist = Spot.objects.filter(spot_area__area_country=country_id)
    context = {'country': p, 'country_area_list': arealist, 'spotlist': spotlist}
    return render(request, 'miroutes/country_detail.html', context)

def area_detail(request, area_id):
    p = get_object_or_404(Area, pk=area_id)
    spotlist = p.spot_set.all()
    context = {'area': p, 'area_spot_list': spotlist}
    return render(request, 'miroutes/area_detail.html', context)

def spot_detail(request, spot_id):
    p = get_object_or_404(Spot, pk=spot_id)
    walllist = p.wall_set.all()
    context = {'spot': p, 'spot_wall_list': walllist}
    return render(request, 'miroutes/spot_detail.html', context)

def wall_detail(request, wall_id, route_id):
    from miroutes.forms import RouteEditForm,EditRoute
    p = get_object_or_404(Wall, pk=wall_id)


    if request.POST:
        if route_id != '0':
            route = get_object_or_404(Route, pk=route_id)
            form = RouteEditForm(request.POST,instance=route)
        else:
            form = RouteEditForm(request.POST)
        #import ipdb; ipdb.set_trace()
        form.save()

    routelist = p.route_set.all()
    context = {'wall': p, 'wall_route_list': routelist}
    return render(request, 'miroutes/wall_detail.html', context)



def route_detail(request, route_id):

    p = get_object_or_404(Route, pk=route_id)
    context = {'route': p}
    return render(request, 'miroutes/route_detail.html', context)


def route_edit(request, wall_id, route_id):
    from miroutes.forms import RouteEditForm,EditRoute

    wall = get_object_or_404(Wall, pk=wall_id)
    routelist = wall.route_set.all()
    routelistdraw = routelist.exclude(pk=route_id)


    route = get_object_or_404(Route, pk=route_id)


    if request.POST:
       form = RouteEditForm(request.POST,instance=route)
       #import ipdb; ipdb.set_trace()
       form.save()



    else:
        form = RouteEditForm(instance = route)


    context = {'wall': wall, 'wall_route_list_draw': routelistdraw, 'wall_route_list': routelist, 'route_selected': route, 'form': form}
    return render(request, 'miroutes/route_edit.html', context)



def route_add(request, wall_id):
    from miroutes.forms import RouteEditForm

    wall = get_object_or_404(Wall, pk=wall_id)
    routelist = wall.route_set.all()


    if request.POST:
        pass

    else:
         form = RouteEditForm()

    context = {'wall': wall, 'wall_route_list': routelist, 'form': form}
    return render(request, 'miroutes/route_add.html', context)

