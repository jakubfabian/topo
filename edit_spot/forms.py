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
