from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

app_name = 'reports'
urlpatterns = [
    url(r'^$', views.get_reports, name='index'),
    url(r'^(?P<report_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<app_id>[0-9]+)/icon$', views.get_app_icon, name='get_app_icon'),
    url(r'^apps/$', views.get_all_apps, name='get_all_apps'),
    url(r'^stats/$', RedirectView.as_view(pattern_name='trackers:get_stats', permanent=False)),
    url(r'^search/(?P<handle>.+)/$', views.get_reports, name='search_by_handle'),
    url(r'^by_tracker/$', views.by_tracker, name='by_tracker'),
    url(r'^(?P<handle>.+)/latest/$', views.detail, name='get_latest'),
]
