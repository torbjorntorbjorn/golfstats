from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  DeleteView,)

from games.models import Game

urlpatterns = patterns('',
    url(r'^games/$', ListView.as_view(
        model=Game,
        context_object_name="games",
    ), name="golfstats-games-games"),

    url(r'^games/create/$', CreateView.as_view(
        model=Game,
        success_url=reverse_lazy('golfstats-games-games'),
    ), name="golfstats-games-games-create"),

    url(r'^games/(?P<pk>\d+)/$', DetailView.as_view(
        model=Game,
        context_object_name="game",
    ), name="golfstats-games-games-detail"),

    url(r'^games/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Game,
        context_object_name="game",
        success_url=reverse_lazy('golfstats-games-games'),
    ), name="golfstats-games-games-delete"),
)
