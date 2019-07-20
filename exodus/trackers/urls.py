from django.conf.urls import url

from . import views

app_name = 'trackers'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^graph$', views.graph, name='graph'),
    url(r'^(?P<tracker_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^stats/$', views.get_stats, name='get_stats'),
]
