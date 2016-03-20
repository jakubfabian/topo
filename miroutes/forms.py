from django import forms
from django.views.generic import UpdateView
from leaflet.forms.widgets import LeafletWidget

from .models import Route, RouteGeometry

class RouteGeometryEditForm(forms.ModelForm):
  class Meta:
    model = RouteGeometry
    fields = ('geom',)
    w = LeafletWidget()

class RouteEditForm(forms.ModelForm):
  class Meta:
    model = Route
    fields = ('route_name', 'route_grade')

class WallImgUploadForm(forms.Form):
  """
  Form to upload an image file for a specific wall.
  """
  image = forms.ImageField()

  
