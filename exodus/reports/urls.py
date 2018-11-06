from django.conf.urls import url

from . import views

app_name = 'reports'
urlpatterns = [
    url(r'^all/$', views.get_reports, name='index'),
    url(r'^no_trackers/$', views.get_reports_no_trackers, name='get_reports_no_trackers'),
    url(r'^most_trackers/$', views.get_reports_most_trackers, name='get_reports_most_trackers'),
    url(r'^(?P<report_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<app_id>[0-9]+)/icon$', views.get_app_icon, name='get_app_icon'),
    url(r'^apps/$', views.get_all_apps, name='get_all_apps'),
    url(r'^stats/$', views.get_stats, name='get_stats'),
    url(r'^search/(?P<handle>.+)$', views.get_reports, name='search_by_handle'),
]
