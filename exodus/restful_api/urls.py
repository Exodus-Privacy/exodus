from django.conf.urls import url
from restful_api import views
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    url(r'^report/(?P<r_id>[0-9]+)/$', views.get_report_infos),
    url(r'^apk/(?P<r_id>[0-9]+)/$', views.get_apk),
    url(r'^pcap/(?P<r_id>[0-9]+)/$', views.upload_pcap),
    url(r'^flow/(?P<r_id>[0-9]+)/$', views.upload_flow),
    url(r'^reports$', views.get_all_reports),
    url(r'^report/(?P<r_id>[0-9]+)/details$', views.get_report_details),
    url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^search/(?P<handle>[a-z|.]+)$', views.search_handle, name = 'search_handle'),
]
