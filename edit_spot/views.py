"""Views related to the *edit* workflow, i.e., pages on which
route/wall/spot-related content is modified.
"""
from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import permission_required, login_required

from django.core.urlresolvers import reverse

from miroutes.models import Spot
from miroutes.models import Wall
from miroutes.models import Route
from miroutes.models import RouteGeometry
from miroutes.models import GRADE_CHOICES

from .forms import SpotForm, RouteForm, WallForm, PolylineForm


@permission_required('miroutes.spot.can_change')
def index(request):
    """
    Main view for editing spots
    """
    spot_listing = Spot.objects.order_by('name')
    context = {'spot_listing': spot_listing}
    return render(request, 'edit_spot/index.html', context)


@permission_required('miroutes.wall.can_change')
def wall_index(request, spot_id):
    """
    Display all walls on spot and give user possibility to create new ones
    """
    spot = get_object_or_404(Spot, pk=spot_id)

    wall_listing = Wall.objects.filter(spot__id=spot_id).order_by('name')
    context = {'wall_listing': wall_listing,
               'spot': spot,
               'show_edit_pane': True}
    if request.session.get('last_wall_id'):
        context['last_wall_id'] = request.session['last_wall_id']
    return render(request, 'edit_spot/wall_index.html', context)


@permission_required('miroutes.wall.can_change')
def publish_wall(request, wall_id):
    """
        Publish Wall
    """
    wall = get_object_or_404(Wall, pk=wall_id)
    wall.publish_dev_view()
    wall.is_active = True
    wall.save()
    return redirect(reverse('spot_detail', kwargs={'spot_id': wall.spot.id}))


@permission_required('miroutes.wall.can.change')
def link_routes_to_wall(request, wall_id, **kwargs):
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
    request.session['last_wall_id'] = wall_id

    wallview = wall.dev_view


    spot = wall.spot
    # all routes on the spot
    spotroutelist = spot.route_set.all()

    if request.POST:
        # Get route ids from right hand side list in template
        route_onwall_ids = request.POST.getlist('routes_onwall', None)
        print request.POST, ':: route_onwall_ids', route_onwall_ids

        # Jones Wed 28 Sep TODO: check why there was a check for 0 routes, forbidden to unselect all?
        # if len(route_onwall_ids) != 0:

        # Routes which are moved from the spot's route pool to this wall are added
        routes_toadd = spotroutelist.filter(pk__in=route_onwall_ids).exclude(walls=wallview)
        for route in routes_toadd:
            geom_obj = RouteGeometry(route=route, on_wallview=wallview, geom=None)
            geom_obj.save()

        # Routes that are not on wall list anymore get detached
        routes_todel = wallview.route_set.exclude(pk__in=route_onwall_ids)
        for route in routes_todel:
            rg = route.routegeometry_set.filter(on_wallview=wallview)
            rg.delete()

    # annotate with walls (dev walls get an asterisk on front)
    active_walldict = {}
    for route in spotroutelist:
        active_walllist = [view.wall.name for view in route.walls.filter(is_dev=False)]
        dev_walllist = ['*'+view.wall.name for view in route.walls.filter(is_dev=True)]
        active_walldict[route.id] = ", ".join(dev_walllist + active_walllist)

    # routes on the dev view
    wallroutelist = wallview.route_set.all()

    # take relative complement for spotroutelist:
    # i.e. remove all routes in spotroutelist that are already at wall
    spotroutelist = spotroutelist.exclude(walls=wallview)

    # all active walls on the spot without the currently selected wall
    spotwalllist = Wall.active_objects.all()
    spotwalllist = spotwalllist.exclude(pk=wall.id)

    # routes that are not on an active wall
    # spotroutesnotonwall = spotroutelist.filter(walls=None)

    # also get all geoms asociated with wall routes
    wallroutegeomlist = wallview.routegeometry_set.all()

    # TODO: in order to use them consecutively in template, shouldnt we order them by something?

    context = {'spot': wall.spot,
               'spot_walllist': spotwalllist,
               'wall': wall,
               'wallview': wallview,
               'spot_routelist': spotroutelist,
               'wall_routelist': wallroutelist,
               'active_walldict': active_walldict,
               'show_edit_pane': True}

    if request.session.get('last_wall_id'):
        context['last_wall_id'] = request.session['last_wall_id']

    return render(request, 'edit_spot/link_routes_to_wall.html', context)


@permission_required('miroutes.wall.can_add')
def add_wall(request, spot_id, **kwargs):
    """
    Adding a new wall.
    """

    spot = get_object_or_404(Spot, pk=spot_id)

    if request.method == 'POST':

        form = WallForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return wall_index(request, spot.pk)
    else:
        form = WallForm(initial={'spot': spot})

    wall_list = spot.wall_set.all().order_by('name')

    context = {
        'editing': False,
        'spot': spot,
        'wall_list': wall_list,
        'show_edit_pane': True,
        'form': form
    }
    return render(request, 'edit_spot/edit_wall.html', context)

@permission_required('miroutes.wall.can_edit')
def edit_wall(request, wall_id, **kwargs):
    """
    Editing a wall.
    """

    wall = get_object_or_404(Wall, pk=wall_id)
    request.session['last_wall_id'] = wall_id
    spot = wall.spot

    if request.method == 'POST':

        form = WallForm(request.POST, request.FILES, instance=wall)
        if form.is_valid():
            form.save()
            return wall_index(request, spot.pk)
    else:
        form = WallForm(initial={'spot': spot}, instance=wall)

    wall_list = spot.wall_set.exclude(pk=wall_id).order_by('name')

    context = {
        'editing': True,
        'wall': wall,
        'spot': spot,
        'wall_list': wall_list,
        'show_edit_pane': True,
        'form': form
    }

    if request.session.get('last_wall_id'):
        context['last_wall_id'] = request.session['last_wall_id']

    return render(request, 'edit_spot/edit_wall.html', context)


@permission_required('miroutes.spot.can_add')
def add_spot(request, **kwargs):
    """
    Adding a new spot.
    """
    request.session.pop('last_wall_id', None)

    if request.method == 'POST':

        form = SpotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('edit_spot_index'))
    else:
        form = SpotForm()

    spot_list = Spot.objects.order_by('name')

    context = {
        'editing': False,
        'spot_list': spot_list,
        'show_edit_pane': True,
        'form': form
    }
    return render(request, 'edit_spot/add_spot.html', context)


@permission_required('miroutes.spot.can_change')
def edit_spot(request, spot_id):
    """
    Alter location and meta info of spot
    """

    request.session.pop('last_wall_id', None)

    spot_list = Spot.objects.exclude(pk=spot_id).order_by('name')
    spot = get_object_or_404(Spot, pk=spot_id)

    if request.method == 'POST':
        form = SpotForm(request.POST, instance=spot)

        if form.is_valid():
            form.save()

    else:
        form = SpotForm(instance=spot)

    context = {'spot': spot,
               'spot_list': spot_list,
               'show_edit_pane': True,
               'form': form}

    return render(request, 'edit_spot/edit_spot.html', context)


def get_grade_choices(spot):
    """
    We use the spot's grade system entry to limit the possible grade choices for routes
    """
    grade_choices = filter(lambda x: x[0]//100 == spot.grade_system, GRADE_CHOICES)
    return grade_choices


@permission_required('miroutes.spot.can_add')
def add_route(request, spot_id, **kwargs):
    """
    Adding a new Route.
    """
    spot = get_object_or_404(Spot, pk=spot_id)

    if request.method == 'POST':

        form = RouteForm(request.POST, grade_choices=get_grade_choices(spot))
        if form.is_valid():
            form.save()
    else:
        form = RouteForm(initial={'spot': spot}, grade_choices=get_grade_choices(spot))

    route_list = spot.route_set.all().order_by('name')

    context = {
        'editing': False,
        'spot': spot,
        'route_list': route_list,
        'form': form,
        'show_edit_pane': True
    }

    if request.session.get('last_wall_id'):
        context['last_wall_id'] = request.session['last_wall_id']

    return render(request, 'edit_spot/edit_routepool.html', context)

@permission_required('miroutes.spot.can_add')
def edit_route(request, route_id, **kwargs):
    """
    Adding a new Route.
    """
    route = get_object_or_404(Route, pk=route_id)
    spot = route.spot

    if request.method == 'POST':

        form = RouteForm(request.POST, instance=route, grade_choices=get_grade_choices(spot))
        if form.is_valid():
            form.save()
    else:
        form = RouteForm(initial={'spot': spot}, instance=route, grade_choices=get_grade_choices(spot))
        # form = RouteForm()

    route_list = spot.route_set.all().order_by('name')

    context = {
        'editing': True,
        'spot': spot,
        'route': route,
        'route_list': route_list,
        'form': form,
        'show_edit_pane': True
    }

    if request.session.get('last_wall_id'):
        context['last_wall_id'] = request.session['last_wall_id']

    return render(request, 'edit_spot/edit_routepool.html', context)


@permission_required('miroutes.wall.can.change')
def draw_routes(request, wall_id, **kwargs):
    """Draw route geometries on a wall.

    Select all routegeometries on a wall. Draw existing geometry strings.

    """
    wall = get_object_or_404(Wall, pk=wall_id)
    request.session['last_wall_id'] = wall_id
    wallview = wall.dev_view
    wallroutegeomquery = wallview.routegeometry_set.all()

    if request.POST:
        polyline_forms = []
        for geom in wallroutegeomquery:
            polyline_forms.append(PolylineForm(request.POST, instance=geom, prefix=geom.pk))
        for form in polyline_forms:
            if form.is_valid():
                form.save()
                

    polyline_forms = []
    for geom in wallroutegeomquery:
        polyline_forms.append(PolylineForm(instance=geom, prefix=geom.pk))
        
    # also get all geoms asociated with wall routes
    wallroutegeomlist = list(wallview.routegeometry_set.all())

    # annotate with a label
    anchorpointlist = []
    for geom in wallroutegeomlist:
        try:
            anchorpointlist.append([geom.anchorpoint[0], geom])
        except:
            anchorpointlist.append([None, geom])
    # sort, None values first
    anchorpointlist = sorted(anchorpointlist, key=lambda x: (x[0] is not None, x[0]))
    for pos, entry in enumerate(anchorpointlist):
        if entry[0]:
            entry[1].label = pos + 1
        else:
            entry[1].label = '*'
        wallroutegeomlist[pos] = entry[1]


    context = {'wall': wall,
               'spot': wall.spot,
               'wallview': wallview,
               'wall_routegeomlist': wallroutegeomlist,
               'polyline_forms': polyline_forms,
               'show_edit_pane': True}

    if request.session.get('last_wall_id'):
        context['last_wall_id'] = request.session['last_wall_id']

    return render(request, 'edit_spot/draw_routes.html', context)
