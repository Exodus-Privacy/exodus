from django.urls import path

from . import views

app_name = 'trackers'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:tracker_id>/', views.detail, name='detail'),
    path('stats/', views.get_stats, name='get_stats'),
    path('graph/', views.graph, name='graph'),
    path('details/', views.TrackersListView.as_view(), name='all_details'),
    path('api_key/', views.new_api_key, name='new_api_key'),
]
