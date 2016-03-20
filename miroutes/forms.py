from django import forms
from django.views.generic import UpdateView
from leaflet.forms.widgets import LeafletWidget

from .models import Route, Spot


class RouteEditForm(forms.ModelForm):
  class Meta:
    model = Route
    fields = ('route_name', 'route_grade', 'route_walls')
    w = LeafletWidget()
    #widgets = {'geom': forms.HiddenInput}

class EditRoute(UpdateView):
  model = Route
  form_class = RouteEditForm
  template_name = 'miroutes/route_edit.html'

class SpotEditForm(forms.ModelForm):
  class Meta:
    model = Spot
    fields = ('spot_name','geom')
    widgets = {'geom': LeafletWidget()}

class EditSpot(UpdateView):
  model = Spot
  form_class = SpotEditForm
  template_name = 'miroutes/spot_edit.html'

class WallImgUploadForm(forms.Form):
  """
  Form to upload an image file for a specific wall.
  """
  image = forms.ImageField()

  
