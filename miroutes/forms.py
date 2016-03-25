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
        exclude = ('route_wall',)

    def __init__(self, spotGradeSystem=0, *args, **kwargs):
        super(RouteEditForm, self).__init__(*args, **kwargs)
        self.fields['route_grade'] = forms.ChoiceField(choices = Route.GRADE_CHOICES[spotGradeSystem])    


class SpotEditForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ('spot_name', 'geom')
        widgets = {'geom': LeafletWidget()}


class WallImgUploadForm(forms.Form):
    """
    Form to upload an image file for a specific wall.
    """
    image = forms.ImageField()
    
