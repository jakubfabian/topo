from django import forms
from django.views.generic import UpdateView
from leaflet.forms.widgets import LeafletWidget

from .models import Route
from .models import Wall

class RouteEditForm(forms.ModelForm):
  class Meta:
    model = Route
    fields = ('geom', 'route_name', 'route_grade', 'route_wall')
    w = LeafletWidget()
    #widgets = {'geom': forms.HiddenInput}

class EditRoute(UpdateView):
  model = Route
  form_class = RouteEditForm
  template_name = 'miroutes/route_edit.html'

class WallImgUploadForm(forms.Form):
  """
  Form to upload an image file for a specific wall.
  """
  image = forms.ImageField()

  
