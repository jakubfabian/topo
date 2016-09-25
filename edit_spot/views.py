from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import permission_required, login_required

from django.core.urlresolvers import reverse

from miroutes.models import Spot
from miroutes.models import Wall
from miroutes.models import Route

from .forms import SpotForm

@permission_required('miroutes.spot.can_change')
def index(request):
    """
    Main view for editing spots
    """
    spot_listing = Spot.objects.order_by('name')
    context = {'spot_listing': spot_listing}
    return render(request, 'edit_spot/index.html', context)


@permission_required('miroutes.spot.can_add')
def add_spot(request, **kwargs):
    """
    Adding a new spot.
    """
    if request.method == 'POST':

        form = SpotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('edit_spot_index'))
    else:
        form = SpotForm()

    spot_list = Spot.objects.order_by('name')

    context = {
        'spot_list': spot_list,
        'form' : form
    }
    return render(request, 'edit_spot/add_spot.html', context)


@permission_required('miroutes.spot.can_change')
def edit_spot(request, spot_id):
    """
    Alter location and meta info of spot
    """
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
            'form': form}
    return render(request, 'edit_spot/edit_spot.html', context)
