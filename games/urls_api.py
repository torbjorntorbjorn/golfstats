from django.conf.urls.defaults import patterns, url
from piston.resource import Resource

from games.handlers import GameHandler, GameHoleHandler


game_handler = Resource(GameHandler)
gamehole_handler = Resource(GameHoleHandler)


urlpatterns = patterns('',
    url(r'^games/$', game_handler),
    url(r'^games/(?P<pk>\d+)/$', game_handler),
    url(r'^games/(?P<pk>\d+)/gameholes/$', gamehole_handler),
)
