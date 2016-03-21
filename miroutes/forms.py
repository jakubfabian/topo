from django import forms
from leaflet.forms.widgets import LeafletWidget

from .models import Route, RouteGeometry, Spot

class RouteGeometryEditForm(forms.ModelForm):
  class Meta:
    model = RouteGeometry
    fields = ('geom',)
    w = LeafletWidget()

class RouteEditForm(forms.ModelForm):
  class Meta:
    model = Route
    fields = ('route_name', 'route_grade')

class SpotEditForm(forms.ModelForm):
  class Meta:
    model = Spot
    fields = ('spot_name','geom')
    widgets = {'geom': LeafletWidget()}

class WallImgUploadForm(forms.Form):
  """
  Form to upload an image file for a specific wall.
  """
  image = forms.ImageField()

  
