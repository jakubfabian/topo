import ipdb

from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.http import HttpResponse

from miroutes.models import Country
from miroutes.models import Area
from miroutes.models import Spot
from miroutes.models import Wall
from miroutes.models import Route
from miroutes.models import RouteGeometry

from miroutes.forms import WallImgUploadForm




def index(request):
    country_listing = Country.objects.order_by('country_name')[:5]
    area_listing = Area.objects.order_by('area_name')
    spot_listing = Spot.objects.order_by('spot_name')
    wall_listing = Wall.objects.filter(is_active=True).order_by('wall_name')
    route_listing = Route.objects.order_by('route_name')
    context = {'country_listing': country_listing, 'area_listing': area_listing, 'spot_listing': spot_listing, 'wall_listing': wall_listing, 'route_listing': route_listing}
    return render(request, 'miroutes/index.html', context)


def country_detail(request, country_id, **kwargs):
    p = get_object_or_404(Country, pk=country_id)
    arealist = p.area_set.all()
    spotlist = Spot.objects.filter(spot_area__area_country=country_id)
    context = {'country': p, 'country_area_list': arealist, 'spotlist': spotlist}
    return render(request, 'miroutes/country_detail.html', context)

def area_detail(request, area_id, **kwargs):
    p = get_object_or_404(Area, pk=area_id)
    spotlist = p.spot_set.all()
    context = {'area': p, 'area_spot_list': spotlist}
    return render(request, 'miroutes/area_detail.html', context)

def spot_detail(request, spot_id, **kwargs):
    """
    For a specific spot, get a list of walls that are contained within.
    Decide if all or just active ones are given to the template to render.
    """
    p = get_object_or_404(Spot, pk=spot_id)
    walllist = p.wall_set

    if not request.session.get('show_inactive', False):
        walllist = walllist.filter(is_active=True)

    walllist = walllist.order_by('wall_name')

    context = {'spot': p, 'spot_wall_list': walllist}
    return render(request, 'miroutes/spot_detail.html', context)


def add_wall(request, spot_id, **kwargs):
    """
    """
    spot = get_object_or_404(Spot, pk=spot_id)
    walllist = spot.wall_set

    if not request.session.get('show_inactive', False):
        walllist = walllist.filter(is_active=True)

    walllist = walllist.order_by('wall_name')

    if request.POST:
        pass

    context = {'spot': spot, 'spot_wall_list': walllist}
    return render(request, 'miroutes/add_wall.html', context)


def toggle_show_inactive(request):
    """
    Save a value called show_inactive in session dict
    which is used to blend in blend out inactive spots and walls
    i.e. controls if you are in manage mode or just a regular visitor

    Once we changed the value of show_inactive,
    just return to the url that was given with 
    the request tag ''from''
    or if none was given, go back too root
    """
    from django.shortcuts import redirect
    request.session['show_inactive'] = not request.session.get('show_inactive', False)
    return redirect( request.GET.get('from', '/') )


def wall_detail(request, wall_id, **kwargs):
    from miroutes.forms import RouteEditForm
    wall = get_object_or_404(Wall, pk=wall_id)

    routegeomlist = wall.routegeometry_set.all()
    context = {'wall': wall, 'wall_route_geom_list': routegeomlist}
    return render(request, 'miroutes/wall_detail.html', context)


def route_detail(request, route_id, **kwargs):
    p = get_object_or_404(Route, pk=route_id)
    context = {'route': p}
    return render(request, 'miroutes/route_detail.html', context)


def route_edit(request, wall_id, route_id, **kwargs):
    from miroutes.forms import RouteEditForm, RouteGeometryEditForm

    wall = get_object_or_404(Wall, pk=wall_id)
    routegeomlist = wall.routegeometry_set.all()

    routegeomlistdraw = routegeomlist.exclude(route__id=route_id)
    routegeom = get_object_or_404(RouteGeometry, route__id=route_id)

    if request.POST:
        routeform = RouteEditForm(request.POST,instance=routegeom.route)
        routegeomform = RouteGeometryEditForm(request.POST,instance=routegeom)
        if routeform.is_valid() and routegeomform.is_valid:
            routeform.save()
            routegeomform.save()
            messages.add_message(request, messages.SUCCESS, 'Successfully saved route.')
            
        
    routeform = RouteEditForm(instance=routegeom.route)
    routegeomform = RouteGeometryEditForm(instance=routegeom)


    context = {'wall': wall, 'wall_routegeom_list_draw': routegeomlistdraw, 'wall_routegeom_list': routegeomlist, 'routegeom_selected': routegeom, 'route_form': routeform, 'routegeom_form':routegeomform}
    return render(request, 'miroutes/route_edit.html', context)



def route_add(request, wall_id, **kwargs):
    from django.core.urlresolvers import reverse
    from django.http import HttpResponseRedirect

    wall = get_object_or_404(Wall, pk=wall_id)
    newroute = Route(route_spot=wall.wall_spot,
                     route_name='Insert Route Name Here!')
    newroute.save()

    geom = {"type":"LineString","coordinates":[[116,-12.1875],[100,-10.1875]]}
    routegeom = RouteGeometry(on_wall=wall, route=newroute, geom=geom)
    routegeom.save()

    kwargs['route_id'] = newroute.id
    kwargs['wall_id'] = wall_id

    return HttpResponseRedirect(reverse('route_edit', kwargs=kwargs))


def wall_img_provide(request, wall_id, **kwargs):
    old_wall = get_object_or_404(Wall, pk=wall_id)

    if request.POST:
        form = WallImgUploadForm(request.POST, request.FILES)
        if form.is_valid():
            w = Wall(wall_name=old_wall.wall_name, wall_spot=old_wall.wall_spot, geom=old_wall.geom)
            w.background_img = form.cleaned_data['image']
            w.save()
            context = {'wall': w, 'wall_route_list': []}
            return render(request, 'miroutes/wall_detail.html', context)
    else:
        form = WallImgUploadForm()
        return render(request, 'miroutes/wall_upload.html', {'form': form})

