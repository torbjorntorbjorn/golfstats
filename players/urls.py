from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  DeleteView,
                                  UpdateView,)

from players.models import Player
from players.views import stats

urlpatterns = patterns('',
    url(r'^players/$', ListView.as_view(
        model=Player,
        context_object_name="players",
    ), name="golfstats-players-players"),

    url(r'^players/create/$', CreateView.as_view(
        model=Player,
        success_url=reverse_lazy('golfstats-players-players'),
    ), name="golfstats-players-players-create"),

    url(r'^players/(?P<pk>\d+)/$', DetailView.as_view(
        model=Player,
        context_object_name="player",
    ), name="golfstats-players-players-detail"),

    url(r'^players/(?P<pk>\d+)/stats/$', stats,
        name="golfstats-players-players-stats"),

    url(r'^players/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Player,
        context_object_name="player",
        success_url=reverse_lazy('golfstats-players-players'),
    ), name="golfstats-players-players-edit"),

    url(r'^players/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Player,
        context_object_name="player",
        success_url=reverse_lazy('golfstats-players-players'),
    ), name="golfstats-players-players-delete"),
)
