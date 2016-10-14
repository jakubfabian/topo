import json
from django import forms

from miroutes.models import Spot
from miroutes.models import Route
from miroutes.models import RouteGeometry
from miroutes.models import Wall
from django.core.exceptions import ValidationError

class SpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ('name',
                  'description',
                  'geom',
                  'grade_system',
                  'approach',
                  'approach_time',
                  'parking_geom',
                  'parking_description')
        widgets = {'geom': forms.HiddenInput(),
                   'parking_geom': forms.HiddenInput(),
                   'description': forms.widgets.Textarea(attrs={'cols': '30', 'rows': '5'}),
                   'approach': forms.widgets.Textarea(attrs={'cols': '30', 'rows': '4'}),
                   'parking_description': forms.widgets.Textarea(attrs={'cols': '30', 'rows': '4'})}


class WallForm(forms.ModelForm):
    class Meta:
        model = Wall
        exclude = ('thumbnail_img', 'is_active', 'spot',)
        widgets = {'geom': forms.HiddenInput()}


class RouteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        grade_choices = kwargs.pop('grade_choices')
        super(RouteForm, self).__init__(*args, **kwargs)
        print 'In forms',grade_choices
        self.fields['grade'] = forms.ChoiceField(choices=grade_choices)
    class Meta:
        model = Route
        exclude = ('climbers','walls')
        widgets = {'spot': forms.HiddenInput()}


class PolylineForm(forms.ModelForm):
    class Meta:
        model = RouteGeometry
        fields = ('geom',)
        widgets = {'geom': forms.HiddenInput()}

    def clean(self):
        # we do not call the parents clean function which seems to be corrupt
        geomjson = self.cleaned_data.get('geom')

        if not geomjson:
            # if the field is not set we do not care
            return self.cleaned_data

        if geomjson.get('type') == 'LineString':
            if geomjson.has_key('coordinates'):
                return self.cleaned_data
            else:
                raise ValidationError(_('JSON contains no coordinates: %s') % geomjson)
        else:
            raise ValidationError(_('JSON does not represent a Linestring object: %s') % geomjson)


