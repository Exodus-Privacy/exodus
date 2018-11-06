from django.conf.urls import url

from search.views import SearchView

app_name = 'search'
urlpatterns = [
    url(r'^$', SearchView.as_view(), name='search'),
]
