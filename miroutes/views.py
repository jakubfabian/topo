import ipdb
from django.core.urlresolvers import reverse

from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.http import HttpResponse, JsonResponse

from miroutes.models import Country
from miroutes.models import Area
from miroutes.models import Spot
from miroutes.models import Wall
from miroutes.models import WallView
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
    wall_listing = Wall.active_objects.order_by('wall_name')
    route_listing = Route.objects.order_by('route_name')
    context = {'country_listing': country_listing,
               'area_listing': area_listing,
               'spot_listing': spot_listing,
               'wall_listing': wall_listing,
               'route_listing': route_listing}
    return render(request, 'miroutes/index.html', context)


def country_detail(request, country_id, **kwargs):
    """
    Country detail view.
    """
    country = get_object_or_404(Country, pk=country_id)
    arealist = country.area_set.all()
    spotlist = Spot.objects.filter(spot_area__area_country=country_id)
    context = {'country': country, 'country_area_list': arealist, 'spotlist': spotlist}
    return render(request, 'miroutes/country_detail.html', context)


def area_detail(request, area_id, **kwargs):
    """
    Area detail view.
    """
    area = get_object_or_404(Area, pk=area_id)
    spotlist = area.spot_set.all()
    context = {'area': area, 'area_spot_list': spotlist}
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


def spot_add(request, area_id, **kwargs):
    """
    Adding a new spot.
    """
    area = get_object_or_404(Area, pk=area_id)

    if request.POST:
        new_spot = Spot()
        new_spot.spot_name = request.POST.get('spot_name')
        new_spot.spot_area = area
        new_spot.geom = {'coordinates': [
            float(request.POST.get('spot_lng')), float(request.POST.get('spot_lat'))]
            , 'type': 'Point'}
        new_spot.save()

        return redirect(reverse('area_detail', args=(area_id)))

    spot_list = area.spot_set.all()

    context = {
        'area': area,
        'spot_list': spot_list
    }
    return render(request, 'miroutes/spot_add.html', context)


def wall_add(request, spot_id, **kwargs):
    """
    Add a wall to a spot.
    """

    spot = get_object_or_404(Spot, pk=spot_id)


    if request.POST:
        new_wall = Wall()
        new_wall.wall_name = request.POST.get('wall_name')
        new_wall.wall_spot = spot
        new_wall.geom = {'coordinates': [
            float(request.POST.get('wall_lng')), float(request.POST.get('wall_lat'))]
            , 'type': 'Point'}
        new_wall.is_active = True
        new_wall.save()

        return redirect(reverse('spot_detail', args=(spot_id)))

    wall_list = spot.wall_set.all()

    context = {
        'spot': spot,
        'wall_list': wall_list
    }
    return render(request, 'miroutes/wall_add.html', context)


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
    return redirect(request.GET.get('from', '/'))


def wall_detail(request, wall_id, **kwargs):
    """
    Details of a wall and the public view on the wall.
    """
    from miroutes.forms import RouteEditForm
    wall = get_object_or_404(Wall, pk=wall_id)
    wallview = wall.pub_view

    routegeomlist = wallview.routegeometry_set.all()
    context = {'wall': wall,
               'wallview': wallview,
               'wall_route_geom_list': routegeomlist}
    return render(request, 'miroutes/wall_detail.html', context)


def route_detail(request, route_id, **kwargs):
    """
    Details of a route object.
    """
    route = get_object_or_404(Route, pk=route_id)
    route_geometries = route.routegeometry_set.all()
    context = {'route': route, 'route_geometries': route_geometries}
    return render(request, 'miroutes/route_detail.html', context)


def search(request, **kwargs):
    """
    process search request
    """
    search_results = []

    query = request.GET.get('q', "")

    query_results = Area.objects.filter(area_name__icontains=query)
    search_results += [{"text": "Area - " + area.area_name, "id": area.id,
                        "url": reverse('area_detail', kwargs={'area_id': area.id})}
                       for area in query_results]

    query_results = Wall.objects.filter(wall_name__icontains=query)
    search_results += [
        {"text": "Wall - " + wall.wall_name, "id": wall.id, "url": reverse('wall_detail', kwargs={'wall_id': wall.id})}
        for wall in query_results]

    query_results = Spot.objects.filter(spot_name__icontains=query)
    search_results += [
        {"text": "Spot - " + spot.spot_name, "id": spot.id, "url": reverse('spot_detail', kwargs={'spot_id': spot.id})}
        for spot in query_results]

    query_results = Route.objects.filter(route_name__icontains=query)
    search_results += [{"text": "Route - " + route.route_name, "id": route.id,
                        "url": reverse('route_detail', kwargs={'route_id': route.id})} for route in query_results]

    return JsonResponse({"results": search_results})


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

        next = request.GET.get('next', None)
        if routeform.is_valid():
            routeform.save()
            messages.add_message(request, messages.SUCCESS, 'Successfully saved route.')
            if next:
                return redirect(next)

    routeform = RouteEditForm(instance=route)
    routeform.fields['route_grade'] = forms.ChoiceField(
        choices=Route.GRADE_CHOICES[route.route_spot.spot_area.area_grade_system])

    context = {'route': route, 'route_form': routeform, 'from': request.GET.get('from', None)}
    return render(request, 'miroutes/route_edit.html', context)


def wall_edit(request, wall_id, **kwargs):
    """
    Edit the development WallView of a wall.
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
    wallview = wall.dev_view

    # routes on the dev view
    wallroutelist = wallview.route_set.all()

    spot = wall.wall_spot
    # all routes on the spot
    spotroutelist = spot.route_set.all()

    if request.POST:
        # Get route ids from right hand side list in template
        route_onwall_ids = request.POST.getlist('routes_onwall', None)
        print request.POST, ':: route_onwall_ids', route_onwall_ids
        if len(route_onwall_ids) != 0:
            # Routes which are moved from the spot's route pool to this wall are added
            routes_toadd = spotroutelist.filter(pk__in=route_onwall_ids).exclude(route_walls=wallview)
            for route in routes_toadd:
                geom_obj = RouteGeometry(route=route, on_wallview=wallview, geom=None)
                geom_obj.save()

            # Routes that are not on wall list anymore get detached
            routes_todel = wallroutelist.exclude(pk__in=route_onwall_ids)
            for route in routes_todel:
                rg = route.routegeometry_set.filter(on_wallview=wallview)
                rg.delete()

        for key in request.POST.keys():
            if key.startswith('routegeomid_'):
                geomstr = request.POST.get(key)
                rgid = key.split('_')[1]
                geom_obj = RouteGeometry.objects.get(pk=rgid)
                geom_obj.geom = geomstr
                # import ipdb
                # ipdb.set_trace()
                geom_obj.save()

    # take relative complement for spotroutelist:
    # i.e. remove all routes in spotroutelist that are already at wall
    spotroutelist = spotroutelist.exclude(route_walls=wallview)

    # all active walls on the spot without the currently selected wall
    spotwalllist = Wall.active_objects.all()
    spotwalllist = spotwalllist.exclude(pk=wall.id)

    # routes that are not on an active wall
    spotroutesnotonwall = spotroutelist.filter(route_walls=None)

    # also get all geoms asociated with wall routes
    wallroutegeomlist = wallview.routegeometry_set.all()

    # TODO: in order to use them consecutively in template, shouldnt we order them by something?

    context = {'spot': wall.wall_spot,
               'spot_walllist': spotwalllist,
               'wall': wall,
               'wallview': wallview,
               'spot_routelist': spotroutelist,
               'spot_routes_noton_wall': spotroutesnotonwall,
               'wall_routelist': wallroutelist,
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


def wall_provide_img(request, wall_id, **kwargs):
    wall = get_object_or_404(Wall, pk=wall_id)

    if request.POST:
        form = WallImgUploadForm(request.POST, request.FILES)
        if form.is_valid():
            wall.background_img = form.cleaned_data['image']
            wall.save()
            wall.create_tiles()
            wall.save()
            context = {'wall': wall, 'wall_route_list': []}
            return render(request, 'miroutes/wall_detail.html', context)
    else:
        form = WallImgUploadForm()
        return render(request, 'miroutes/wall_provide_img.html', {'form': form})
