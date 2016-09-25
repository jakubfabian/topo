from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from miroutes.forms import WallImgUploadForm
from miroutes.models import Route
from miroutes.models import RouteGeometry
from miroutes.models import Spot
from miroutes.models import Wall


def index(request):
    """
    Main view for landing page
    """
    spot_listing = Spot.objects.order_by('name')
    wall_listing = Wall.active_objects.order_by('name')
    route_listing = Route.objects.order_by('name')
    context = {'spot_listing': spot_listing,
               'wall_listing': wall_listing,
               'route_listing': route_listing}
    return render(request, 'miroutes/index.html', context)

def spot_detail(request, spot_id, **kwargs):
    """
    For a specific spot, get a list of walls that are contained within.
    Decide if all or just active ones are given to the template to render.
    """
    spot = get_object_or_404(Spot, pk=spot_id)
    walllist = spot.wall_set

    if not request.session.get('show_inactive', False):
        walllist = walllist.filter(is_active=True)

    walllist = walllist.order_by('name')

    context = {'spot': spot, 'spot_wall_list': walllist}
    return render(request, 'miroutes/spot_detail.html', context)


@login_required
@permission_required('miroutes.add_wall', raise_exception=True)
def wall_add(request, spot_id, **kwargs):
    """
    Add a wall to a spot.
    """

    spot = get_object_or_404(Spot, pk=spot_id)

    if request.POST:
        new_wall = Wall()
        new_wall.name = request.POST.get('name')
        new_wall.spot = spot
        new_wall.geom = {'coordinates': [
            float(request.POST.get('wall_lng')), float(request.POST.get('wall_lat'))]
            , 'type': 'Point'}
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


def wall_detail(request, wall_id, wallview=None, **kwargs):
    """
    Details of a wall and the public view on the wall.
    """
    wall = get_object_or_404(Wall, pk=wall_id)

    if wallview is None:
        wallview = wall.pub_view

    routegeomlist = wallview.routegeometry_set.all()
    context = {'wall': wall,
               'wallview': wallview,
               'wall_route_geom_list': routegeomlist}
    return render(request, 'miroutes/wall_detail.html', context)


@login_required
def wall_detail_dev(request, wall_id, **kwargs):
    """
    Details of a wall and the public view on the wall.
    """

    wall = get_object_or_404(Wall, pk=wall_id)
    wallview = wall.dev_view

    return wall_detail(request, wall_id, wallview=wallview)


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

    query_results = Wall.objects.filter(name__icontains=query)
    search_results += [
        {"text": "Wall - " + wall.name, "id": wall.id, "url": reverse('wall_detail', kwargs={'wall_id': wall.id})}
        for wall in query_results]

    query_results = Spot.objects.filter(name__icontains=query)
    search_results += [
        {"text": "Spot - " + spot.name, "id": spot.id, "url": reverse('spot_detail', kwargs={'spot_id': spot.id})}
        for spot in query_results]

    query_results = Route.objects.filter(name__icontains=query)
    search_results += [{"text": "Route - " + route.name, "id": route.id,
                        "url": reverse('route_detail', kwargs={'route_id': route.id})} for route in query_results]

    return JsonResponse({"results": search_results})

@login_required
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
    routeform.fields['grade'] = forms.ChoiceField(
        choices=Route.GRADE_CHOICES[1])

    context = {'route': route, 'route_form': routeform, 'from': request.GET.get('from', None)}
    return render(request, 'miroutes/route_edit.html', context)


@login_required
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

    spot = wall.spot
    # all routes on the spot
    spotroutelist = spot.route_set.all()

    if request.POST:
        # Get route ids from right hand side list in template
        route_onwall_ids = request.POST.getlist('routes_onwall', None)
        print request.POST, ':: route_onwall_ids', route_onwall_ids
        if len(route_onwall_ids) != 0:
            # Routes which are moved from the spot's route pool to this wall are added
            routes_toadd = spotroutelist.filter(pk__in=route_onwall_ids).exclude(walls=wallview)
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
    spotroutelist = spotroutelist.exclude(walls=wallview)

    # all active walls on the spot without the currently selected wall
    spotwalllist = Wall.active_objects.all()
    spotwalllist = spotwalllist.exclude(pk=wall.id)

    # routes that are not on an active wall
    spotroutesnotonwall = spotroutelist.filter(walls=None)

    # also get all geoms asociated with wall routes
    wallroutegeomlist = wallview.routegeometry_set.all()

    # TODO: in order to use them consecutively in template, shouldnt we order them by something?

    context = {'spot': wall.spot,
               'spot_walllist': spotwalllist,
               'wall': wall,
               'wallview': wallview,
               'spot_routelist': spotroutelist,
               'spot_routes_noton_wall': spotroutesnotonwall,
               'wall_routelist': wallroutelist,
               'wall_routegeomlist': wallroutegeomlist}

    return render(request, 'miroutes/wall_edit.html', context)


@login_required
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
    newroute = Route(spot=spot,
                     name='Insert Route Name Here!')
    newroute.save()

    kwargs['route_id'] = newroute.id
    kwargs['spot_id'] = spot_id

    return HttpResponseRedirect("{}?from={}".format(
        reverse('route_edit', kwargs=kwargs), request.GET.get('from', None)))


@login_required
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
    routename = route.name
    route.delete()

    messages.add_message(request, messages.SUCCESS, 'Successfully deleted route {}.'.format(routename))

    return redirect(request.GET.get('from', '/'))


@login_required
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
