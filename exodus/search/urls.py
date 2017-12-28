from django.conf.urls import url

from search.views import SearchView

urlpatterns = [
    url(
        r'^$',
        SearchView.as_view(),
        name = 'search',
    ),
]
