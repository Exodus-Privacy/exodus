from django.conf.urls import url

from . import views

app_name = 'reports'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<report_id>[0-9]+)/$', views.detail, name='detail'),
]