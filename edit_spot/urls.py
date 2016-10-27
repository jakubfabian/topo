from django.conf.urls import *

from edit_spot import views

urlpatterns = [ url(r'^$', views.index, name='edit_spot_index'),

url(r'^spot(?P<spot_id>\d+)/$', views.edit_spot, name='edit_spot'),
url(r'^add_spot$', views.add_spot, name='add_spot'),
url(r'^spot(?P<spot_id>\d+)/add_route$', views.add_route, name='add_route'),
url(r'^spot(?P<spot_id>\d+)/add_parking/(?P<lat>[-+]?\d+\.?\d+)/(?P<lng>[-+]?\d+\.?\d+)$', views.add_parking, name='add_parking'),
url(r'^spot(?P<spot_id>\d+)/delete_parking(?P<parking_id>\d+)$', views.delete_parking, name='delete_parking'),
url(r'^spot(?P<spot_id>\d+)/wall_index$', views.wall_index, name='edit_spot_wall_index'),
url(r'^spot(?P<spot_id>\d+)/add_wall$', views.add_wall, name='add_wall'),

url(r'^wall(?P<wall_id>\d+)/edit_wall$', views.edit_wall, name='edit_wall'),
url(r'^wall(?P<wall_id>\d+)/link_routes_to_wall$', views.link_routes_to_wall, name='link_routes_to_wall'),
url(r'^wall(?P<wall_id>\d+)/draw_routes$', views.draw_routes, name='draw_routes'),
url(r'^wall(?P<wall_id>\d+)/publish_wall$', views.publish_wall, name='publish_wall'),
url(r'^wall(?P<wall_id>\d+)/reset_dev_wall$', views.reset_dev_wall, name='reset_dev_wall'),

url(r'^route(?P<route_id>\d+)/edit_route$', views.edit_route, name='edit_route'),
url(r'^route(?P<route_id>\d+)/del_route$', views.del_route, name='del_route'),
]
