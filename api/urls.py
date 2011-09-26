from django.conf.urls.defaults import patterns, url, include

# URL includes for API
urlpatterns = patterns('',
    url(r'', include('players.urls_api')),
)
