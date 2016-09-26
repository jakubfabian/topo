from django import forms

from miroutes.models import Spot
from miroutes.models import Route
from miroutes.models import Wall


class SpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ('name', 'description', 'geom')
        widgets = {'geom': forms.HiddenInput()}


class WallForm(forms.ModelForm):
    class Meta:
        model = Wall
        exclude = ('',)
    #image = forms.ImageField()

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        exclude = ('climbers','walls')
        widgets = {'spot': forms.HiddenInput()}
