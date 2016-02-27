from django.conf.urls import patterns, url

from miroutes import views

urlpatterns = [ url(r'^$', views.index, name='index'),
    url(r'^(?P<country_id>\d+)/$', views.country_detail, name='country detail'),
    url(r'^\d+/(?P<area_id>\d+)/$', views.area_detail, name='area detail'),
    url(r'^\d+/\d+\/(?P<spot_id>\d+)/$', views.spot_detail, name='spot detail'),
    url(r'^\d+/\d+/\d+/(?P<wall_id>\d+)-(?P<route_id>\d+)/$', views.wall_detail, name='wall detail'),
    url(r'^\d+/\d+/\d+/(?P<wall_id>\d+)-\d+/(?P<route_id>\d+)/edit$', views.route_edit, name='edit route'),
    url(r'^\d+/\d+/\d+/(?P<wall_id>\d+)-\d+/addroute$', views.route_add, name='add route'),
    url(r'^\d+/\d+/\d+/\d+/(?P<route_id>\d+)/$', views.route_detail, name='route detail') ]

