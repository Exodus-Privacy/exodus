from django.conf.urls import url
from restful_api import views
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    url(r'^report/(?P<r_id>[0-9]+)/$', views.get_report_infos),
    url(r'^apk/(?P<r_id>[0-9]+)/$', views.get_apk),
    url(r'^pcap/(?P<r_id>[0-9]+)/$', views.upload_pcap),
    url(r'^flow/(?P<r_id>[0-9]+)/$', views.upload_flow),
    url(r'^reports$', views.get_all_reports),  # deprecated
    url(r'^applications$', views.get_all_applications),
    url(r'^trackers$', views.get_all_trackers),
    url(r'^report/(?P<r_id>[0-9]+)/details$', views.get_report_details),
    url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^search/(?P<handle>.+)/details$', views.search_strict_handle_details, name = 'search_strict_handle_details'),
    url(r'^search/(?P<handle>.+)$', views.search_strict_handle, name = 'search_strict_handle'),
    url(r'^search$', views.search, name = 'search'),
]
