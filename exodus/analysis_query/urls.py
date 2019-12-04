from django.conf import settings
from django.conf.urls import url

from . import views

app_name = 'analysis'
urlpatterns = [
    url(r'^$', views.AnalysisRequestListView.as_view(), name='index'),
    url(r'^submit/$', views.AnalysisRequestView.as_view(), name='submit'),
    url(r'^(?P<r_id>[0-9]+)$', views.wait, name='wait'),
    url(r'^(?P<r_id>[0-9]+)/json$', views.json, name='json'),
]

if settings.ALLOW_APK_UPLOAD:
    urlpatterns.append(url(r'^upload/$', views.upload_file, name='upload'))
