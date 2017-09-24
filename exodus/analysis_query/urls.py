from django.conf.urls import url

from . import views

app_name = 'analysis'
urlpatterns = [
    url(r'^$', views.AnalysisRequestListView.as_view(), name='index'),
    url(r'^submit/$', views.AnalysisRequestView.as_view(), name='submit'),
]