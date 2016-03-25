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

from miroutes.forms import WallImgUploadForm, SpotEditForm




def index(request):
    """
    Main view for landing page
    """
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
    spot = get_object_or_404(Spot, pk=spot_id)
    walllist = spot.wall_set

    if not request.session.get('show_inactive', False):
        walllist = walllist.filter(is_active=True)

    walllist = walllist.order_by('wall_name')

    context = {'spot': spot, 'spot_wall_list': walllist}
    return render(request, 'miroutes/spot_detail.html', context)

def spot_edit(request, spot_id, **kwargs):
    """
    Edit an existing spot.
    """
    spot = get_object_or_404(Spot, pk=spot_id)
    spot_list = spot.spot_area.spot_set.all()
    route_list = spot.route_set.all()

    if request.POST:
        form = SpotEditForm(request.POST, instance=spot)
        form.save()
    else:
        form = SpotEditForm(instance=spot)

    context = {'spot': spot,
               'form': form,
               'spot_list': spot_list,
               'route_list': route_list}
    return render(request, 'miroutes/spot_edit.html', context)


def add_wall(request, spot_id, **kwargs):
    """
    """
    spot = get_object_or_404(Spot, pk=spot_id)
    wall_list = spot.wall_set

    if not request.session.get('show_inactive', False):
        wall_list = wall_list.filter(is_active=True)

    wall_list = wall_list.order_by('wall_name')

    if request.POST:
        pass

    context = {'spot': spot, 'spot_wall_list': wall_list}
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
    route = get_object_or_404(Route, pk=route_id)
    context = {'route': route}
    return render(request, 'miroutes/route_detail.html', context)


def route_edit(request, route_id, **kwargs):
    """
    Edit route object. Accessible via spot details and wall details.
    In this view, only the metadata of a route object should be
    edited (not its geometry).

    Args:
      request: HTTP request
      route_id: the id of the route to edit

    Returns:
      A form that allows to modify the properties of a route.
    
    """
    from miroutes.forms import RouteEditForm
    from django.shortcuts import redirect
    from django import forms
    
    route = get_object_or_404(Route, id=route_id)

    if request.POST:
        routeform = RouteEditForm(request.POST, instance=route)
        routeform.fields['route_grade'] = forms.ChoiceField(
            required=True,
            choices=Route.GRADE_CHOICES[route.route_spot.spot_grade_system])
        next = request.GET.get('next', None)
        if routeform.is_valid():
            routeform.save()
            messages.add_message(request, messages.SUCCESS, 'Successfully saved route.')
            if next:
                return redirect(next)

    routeform = RouteEditForm(instance=route)

    context = {'route': route, 'route_form': routeform, 'from': request.GET.get('from', None)}
    return render(request, 'miroutes/route_edit.html', context)



def wall_edit(request, wall_id, **kwargs):
    """
    Edit the route geometries on a wall.
    If the wall is active, all changes are made on the development
    version of the wall.
    We select one existing route or
    create a new one and draw the geometry.

    Args:
      request: the http request object
      spot_id: the id of the spot as given in the url, see urls.py
      wall_id: the id of the wall as given in the url, see urls.py

    Returns:
      A HTML web page generated from the wall_edit.html template
    """
    wall = get_object_or_404(Wall, pk=wall_id)
    spot = wall.wall_spot

    # we modify the development version of the wall
    # if the wall is active
    if wall.is_active:
        # ... and create the wall if it does not exist
        if wall.theOtherWall is None:
            wall.copyme_to_theOtherWall()
        wall = wall.theOtherWall
    spotroutelist = spot.route_set.all()
    wallroutegeomlist = wall.routegeometry_set.all()

    context = {'wall': wall,
               'spot_routelist': spotroutelist,
               'wall_routegeomlist': wallroutegeomlist}
    
    return render(request, 'miroutes/wall_edit.html', context)

def route_add(request, spot_id, **kwargs):
    """
    Add a route to a spot.

    Args:
      request: http request
      spot_id: the id of the spot as given by the url
    
    Returns:
      A template generated from a form to enter route details
    """
    from django.core.urlresolvers import reverse
    from django.http import HttpResponseRedirect

    spot = get_object_or_404(Spot, id=spot_id)
    newroute = Route(route_spot=spot,
                     route_name='Insert Route Name Here!')
    newroute.save()

    kwargs['route_id'] = newroute.id
    kwargs['spot_id'] = spot_id

    return HttpResponseRedirect("{}?from={}".format(
        reverse('route_edit', kwargs=kwargs), request.GET.get('from', None)))
    

def route_del(request, route_id, **kwargs):
    """
    Delete route from route list and redirect to the page
    provided in the from tag.
    
    Args:
      request: HTTP request
      route_id: id of route to delete
    Returns:
      Redirect to the page url saved in the from tag of the HTTP GET request.
    """
    from django.shortcuts import redirect

    route = get_object_or_404(Route, pk=route_id)
    for routegeom in route.routegeometry_set.all():
        routegeom.delete()
    routename = route.route_name
    route.delete()

    messages.add_message(request, messages.SUCCESS, 'Successfully deleted route {}.'.format(routename))

    return redirect(request.GET.get('from', '/'))


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

