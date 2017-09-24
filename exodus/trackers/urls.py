from django.conf.urls import url

from . import views

app_name = 'trackers'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<tracker_id>[0-9]+)/$', views.detail, name='detail'),
]