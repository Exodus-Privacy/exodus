from django.urls import path
from restful_api import views
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    path('report/<int:r_id>/', views.get_report_infos),
    path('apk/<int:r_id>/', views.get_apk),
    path('reports', views.get_all_reports),  # deprecated
    path('applications', views.get_all_applications),
    path('trackers', views.get_all_trackers),
    path('report/<int:r_id>/details', views.get_report_details),
    path('get_auth_token/', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    path('search/<handle>/details', views.search_strict_handle_details, name='search_strict_handle_details'),
    path('search/<handle>', views.search_strict_handle, name='search_strict_handle'),
    path('search', views.search, name='search'),
]
