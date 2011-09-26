from django.conf.urls.defaults import patterns, url
from piston.resource import Resource

from players.handlers import PlayerHandler


player_handler = Resource(PlayerHandler)


urlpatterns = patterns('',
    url(r'^players/$', player_handler),
    url(r'^players/(?P<pk>\d+)/$', player_handler),
)
