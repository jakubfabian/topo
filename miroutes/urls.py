from django.conf.urls import *

from miroutes import views

urlpatterns = [ url(r'^$', views.index, name='miroutes_index'),

url(r'^spot(?P<spot_id>\d+)/$', views.spot_detail, name='spot_detail'),
url(r'^search/', views.search, name='search'),

url(r'^wall(?P<wall_id>\d+)/dev$', views.wall_detail_dev, name='wall_detail_dev'),
url(r'^wall(?P<wall_id>\d+)/$', views.wall_detail, name='wall_detail'),

url(r'^wall(?P<wall_id>\d+)/route_hist$', views.wall_route_hist, name='wall_route_hist'),

url(r'^route(?P<route_id>\d+)$', views.route_detail, name='route_detail'),

url(r'toggle_show_inactive', views.toggle_show_inactive, name='toggle_show_inactive'),
]
