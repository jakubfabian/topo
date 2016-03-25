from django.conf.urls import patterns, url

from miroutes import views

urlpatterns = [ url(r'^$', views.index, name='index'),
                url(r'^(?P<country_id>\d+)/$', views.country_detail, name='country detail'),
                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)/$', views.area_detail, name='area detail'),
                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)\/(?P<spot_id>\d+)/$', views.spot_detail, name='spot detail'),
                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)\/(?P<spot_id>\d+)/edit$', views.spot_edit, name='edit spot'),
                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)\/(?P<spot_id>\d+)/add_wall$', views.add_wall, name='add wall'),
                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)\/(?P<spot_id>\d+)/route(?P<route_id>\d+)$', views.route_detail, name='route detail'),

url(r'^wall(?P<wall_id>\d+)/$', views.wall_detail, name='wall_detail'),

url(r'^spot(?P<spot_id>\d+)/route_add$', views.route_add, name='route_add'),

url(r'^wall(?P<wall_id>\d+)/route(?P<route_id>\d+)/edit$', views.route_edit, name='route_edit'),

url(r'^wall(?P<wall_id>\d+)/route(?P<route_id>\d+)/del$', views.route_del, name='route_del'),

                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)\/(?P<spot_id>\d+)/(?P<wall_id>\d+)/providewallimg$', views.wall_img_provide, name='provide wall image'),
                url(r'^(?P<country_id>\d+)/(?P<area_id>\d+)\/(?P<spot_id>\d+)/(?P<wall_id>\d+)/edit$', views.wall_edit, name='edit wall'),
                url(r'toggle_show_inactive', views.toggle_show_inactive, name='toggle_show_inactive'),
                ]





