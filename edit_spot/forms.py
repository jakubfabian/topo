from django import forms

from miroutes.models import Spot
from miroutes.models import Route
from miroutes.models import Wall


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
        exclude = ('',)
    #image = forms.ImageField()

GRADE_CHOICES = (
    (
        (1, '4b+'),
        (2, '4c-'),
        (3, '4c'),
        (4, '4c+'),
        (5, '5a-')),
    (
        (1, 'IV-'),
        (2, 'IV'),
        (3, 'IV+'),
        (4, 'V-'),
        (5, 'V')),
    (
        (1, 'S, 4a'),
        (2, 'HS, 4b'),
        (3, 'VS, 4c'),
        (4, 'HVS, 5a'),
        (5, 'E1, 5b')),
    (
        (1, '5.4'),
        (2, '5.5'),
        (3, '5.6'),
        (4, '5.7'),
        (5, '5.8'))
)

class RouteForm(forms.ModelForm):
    def __init__(self, spot, *args, **kwargs):
        super(RouteForm, self).__init__(*args, **kwargs)
        self.fields['grade'] = forms.ChoiceField(choices=GRADE_CHOICES[spot.grade_system])

    class Meta:
        model = Route
        exclude = ('climbers','walls')
        widgets = {'spot': forms.HiddenInput()}
