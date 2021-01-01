from django.conf import settings
from django.urls import path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('', views.AnalysisRequestListView.as_view(), name='index'),
    path('submit/', views.AnalysisRequestView.as_view(), name='submit'),
    path('<int:r_id>/', views.wait, name='wait'),
    path('<int:r_id>/json/', views.json, name='json'),
]

if settings.ALLOW_APK_UPLOAD:
    urlpatterns.append(path('upload/', views.upload_file, name='upload'))
