from django.conf.urls import url

from . import views

app_name = 'reports'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<report_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^apps/$', views.get_all_apps, name='get_all_apps'),
    url(r'^stats/$', views.get_stats, name='get_stats'),
    url(r'^search/(?P<handle>.+)$', views.search_by_handle, name='search_by_handle'),
    # url(r'^refresh_dns/$', views.refreshdns, name='refreshdns'),
]