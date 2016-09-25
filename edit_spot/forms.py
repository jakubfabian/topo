from django import forms

from miroutes.models import Spot


class SpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ('name', 'description', 'geom')
        widgets = {'geom': forms.HiddenInput()}
