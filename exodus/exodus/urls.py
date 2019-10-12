"""exodus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n'))
]
urlpatterns += [
    url(r'^api/', include('restful_api.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
urlpatterns += i18n_patterns(
    url(r'^analysis/', include('analysis_query.urls')),
    url(r'^trackers/', include('trackers.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^$', views.index, name='home'),
    url(r'^info/permissions/$', views.permissions, name='permissions'),
    url(r'^info/trackers/$', views.trackers, name='trackers'),
    url(r'^info/next/$', views.next, name='next'),
    url(r'^info/understand/$', views.understand, name='understand'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler404 = 'exodus.views.page_not_found'
# handler500 = 'exodus.views.page_not_found'
