from django.conf.urls import *

from edit_spot import views

urlpatterns = [ url(r'^$', views.index, name='edit_spot_index'),

url(r'^spot(?P<spot_id>\d+)/$', views.edit_spot, name='edit_spot'),
#url(r'^search/', views.search, name='search'),
url(r'^add_spot$', views.add_spot, name='add_spot'),
# 
# url(r'^wall(?P<wall_id>\d+)/dev$', views.wall_detail_dev, name='wall_detail_dev'),
# url(r'^wall(?P<wall_id>\d+)/$', views.wall_detail, name='wall_detail'),
# url(r'^spot(?P<spot_id>\d+)/wall_add$', views.wall_add, name='wall_add'),
# url(r'^wall(?P<wall_id>\d+)/edit$', views.wall_edit, name='wall_edit'),
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





