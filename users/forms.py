
from django import forms
from django.core import validators
from django.contrib.auth.models import User

def isValidUsername(field_data):
  try:
    User.objects.get(username=field_data)
  except User.DoesNotExist:
    return
  raise validators.ValidationError('The username "%s" is already taken.' % field_data)

class RegistrationForm(forms.Form):
  def save(self, new_data):
    u = User.objects.create_user(new_data['username'], new_data['email'], new_data['password'])
    u.is_active = False
    u.save()
    return u

  username = forms.CharField(label='Benutzername', max_length=30, validators=[isValidUsername,])
  email    = forms.EmailField()
  password = forms.CharField(label='Passwort', widget=forms.PasswordInput)

