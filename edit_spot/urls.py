from django.conf.urls import *

from edit_spot import views

urlpatterns = [ url(r'^$', views.index, name='edit_spot_index'),

url(r'^spot(?P<spot_id>\d+)/$', views.edit_spot, name='edit_spot'),
#url(r'^search/', views.search, name='search'),
url(r'^add_spot$', views.add_spot, name='add_spot'),
url(r'^spot(?P<spot_id>\d+)/add_route$', views.add_route, name='add_route'),
url(r'^route(?P<route_id>\d+)/edit_route$', views.edit_route, name='edit_route'),
url(r'^spot(?P<spot_id>\d+)/wall_index$', views.wall_index, name='edit_spot_wall_index'),
# url(r'^wall(?P<wall_id>\d+)/dev$', views.wall_detail_dev, name='wall_detail_dev'),
# url(r'^wall(?P<wall_id>\d+)/$', views.wall_detail, name='wall_detail'),
 url(r'^spot(?P<spot_id>\d+)/add_wall$', views.add_wall, name='add_wall'),
 url(r'^wall(?P<wall_id>\d+)/link_routes_to_wall$', views.link_routes_to_wall, name='link_routes_to_wall'),
 url(r'^wall(?P<wall_id>\d+)/draw_routes$', views.draw_routes, name='draw_routes'),
 url(r'^wall(?P<wall_id>\d+)/publish_wall$', views.publish_wall, name='publish_wall'),
# 
# url(r'^route(?P<route_id>\d+)$', views.route_detail, name='route_detail'),
# url(r'^spot(?P<spot_id>\d+)/route_add$', views.route_add, name='route_add'),
# url(r'^route(?P<route_id>\d+)/edit$', views.route_edit, name='route_edit'),
# url(r'^route(?P<route_id>\d+)/del$', views.route_del, name='route_del'),
# 
# url(r'^wall(?P<wall_id>\d+)/wall_provide_img$', views.wall_provide_img, name='wall_provide_img'),
# 
# url(r'toggle_show_inactive', views.toggle_show_inactive, name='toggle_show_inactive'),
]





