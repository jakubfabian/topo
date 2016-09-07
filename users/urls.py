from django.conf.urls import *
from django.contrib.auth.views import login, logout

from users import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^confirm/(?P<activation_key>.*)$', views.confirm, name='confirm'),
    url(r'^login/$',  login),
    url(r'^logout/$', logout),
]

