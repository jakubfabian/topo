"""Views for *consumers* of spot/wall/route information."""
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

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
    parking_list = spot.parkinglocation_set.all()
    walllist = spot.wall_set.all()
    print walllist

    if not request.session.get('show_inactive', False):
        walllist = walllist.filter(is_active=True)

    walllist = walllist.order_by('name')

    context = {
        'spot': spot,
        'spot_wall_list': walllist,
        'parking_list': parking_list}
    return render(request, 'miroutes/spot_detail.html', context)


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

    wall.test = 'my magic'
    routegeomlist = wallview.routegeometry_set.all()
    # sort from left to right
    routegeomlist = list(routegeomlist)
    routegeomlist = sorted(routegeomlist, key=lambda x: x.anchorpoint[0])
    # we annotate with the index
    for num, geom in enumerate(routegeomlist):
        geom.label = num + 1 # humans count from 1

    context = {'wall': wall,
               'wallview': wallview,
               'wall_routegeomlist': routegeomlist}
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

    query_results = Wall.objects.filter(name__icontains=query).order_by('name')[:20]
    search_results += [
        {"text": "Wall - " + wall.name, "id": wall.id, "url": reverse('wall_detail', kwargs={'wall_id': wall.id})}
        for wall in query_results]

    query_results = Spot.objects.filter(name__icontains=query).order_by('name')[:20]
    search_results += [
        {"text": "Spot - " + spot.name, "id": spot.id, "url": reverse('spot_detail', kwargs={'spot_id': spot.id})}
        for spot in query_results]

    query_results = Route.objects.filter(name__icontains=query).order_by('name')[:20]
    search_results += [{"text": "Route - " + route.name, "id": route.id,
                        "url": reverse('route_detail', kwargs={'route_id': route.id})} for route in query_results]

    return JsonResponse({"results": search_results})


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
