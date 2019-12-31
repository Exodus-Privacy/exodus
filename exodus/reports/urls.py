from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.get_reports, name='index'),
    path('<int:report_id>/', views.detail, name='detail'),
    path('<int:app_id>/icon/', views.get_app_icon, name='icon'),
    path('stats/', RedirectView.as_view(pattern_name='trackers:get_stats', permanent=False)),
    path('search/<handle>/', views.get_reports, name='search_by_handle'),
    path('<handle>/latest/', views.detail, name='get_latest'),
    path('<handle>/latest/icon/', views.get_app_icon, name='icon_by_handle'),
]
