from django.conf import settings
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

from . import views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('restful_api.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += i18n_patterns(
    path('', views.index, name='home'),
    path('analysis/', include('analysis_query.urls')),
    path('trackers/', include('trackers.urls')),
    path('reports/', include('reports.urls')),
    path('info/permissions/', views.permissions, name='permissions'),
    path('info/trackers/', views.trackers, name='trackers'),
    path('info/next/', views.next, name='next'),
    path('info/understand/', views.understand, name='understand'),
    path('info/organization/', views.organization, name='organization'),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler404 = 'exodus.views.page_not_found'
# handler500 = 'exodus.views.page_not_found'
