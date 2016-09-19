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
        exclude = ('walls',)


class SpotAddForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ('name', 'area', 'geom')
        widgets = {'geom': forms.HiddenInput(), 'area': forms.HiddenInput()}


class WallImgUploadForm(forms.Form):
    """
    Form to upload an image file for a specific wall.
    """
    image = forms.ImageField()
