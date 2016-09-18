from django.shortcuts import render,get_object_or_404
from django import forms

from django.contrib.auth.models import User
from users.forms import RegistrationForm

from django.utils import timezone
import random, sha, datetime
from django.core.mail import send_mail

# Create your views here.
def index(request):
  from django.http import HttpResponse
  return HttpResponse(u'This is the users index page')


def register(request):
#  if request.user.is_authenticated():
#    # They already have an account; don't let them register again
#    return render(request, 'users/register.html', {'has_account': True})
  if request.POST:
    register_form = RegistrationForm(request.POST)
    if register_form.is_valid():

      new_user = User.objects.create_user(register_form.data['username'], register_form.data['email'], register_form.data['password'])
      new_user.is_active=False
      new_user.save()

      # Build the activation key for their account                                                                                                                    
      salt           = sha.new(str(random.random())).hexdigest()[:5]
      activation_key = sha.new(salt+new_user.username).hexdigest()
      key_expires    = timezone.now() + datetime.timedelta(2)

      new_user.userprofile.activation_key = activation_key
      new_user.userprofile.key_expires    = key_expires
      new_user.userprofile.save()

      # Send an email with the confirmation link                                                                                                                      
      email_subject = u'Neuer Nutzer bei Mi-Topo.de'
      email_body = u'Hallo, %s, Vielen Dank dass Sie sich entschieden haben Ihren Teil zu MiTopo beizutragen. \
      Um Ihre Benutzerkennung zu aktivieren, klicken Sie bitte innerhalb der naechsten 2 Tage auf folgenden Link. \
      \n\nhttp://localhost:8000/users/confirm/%s' % (
      new_user.email,
      new_user.userprofile.activation_key,
      )

      send_mail(email_subject,
          email_body,
          'registration@mitopo.de',
          [new_user.email,])


      return render(request, 'users/register.html', {'register_successfully': True, 'form': register_form })
  else:
    register_form = RegistrationForm()

  return render(request, 'users/register.html', {'form': register_form})

def confirm(request, activation_key):
  from users.models import UserProfile
  if request.user.is_authenticated():
    return render(request, 'users/confirm.html', {'has_account': True})

  user_profile = get_object_or_404(UserProfile,    activation_key=activation_key)
  if user_profile.key_expires < timezone.now():
    return render(request, 'users/confirm.html', {'expired': True})

  user_account = user_profile.user
  user_account.is_active = True
  user_account.save()
  return render(request, 'users/confirm.html', {'success': True, 'user_account': user_account})
