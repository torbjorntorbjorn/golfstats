from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  DeleteView,
                                  UpdateView,)

from courses.models import Arena, Tee, Hole

urlpatterns = patterns('',
    url(r'^arenas/$', ListView.as_view(
        model=Arena,
        context_object_name="arenas",
    ), name="golfstats-courses-arenas"),

    url(r'^arenas/create/$', CreateView.as_view(
        model=Arena,
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-create"),

    url(r'^arenas/(?P<pk>\d+)/$', DetailView.as_view(
        model=Arena,
        context_object_name="arena",
    ), name="golfstats-courses-arenas-detail"),

    url(r'^arenas/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Arena,
        context_object_name="arena",
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-detail"),

    url(r'^arenas/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Arena,
        context_object_name="arena",
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-delete"),

    url(r'^tees/$', ListView.as_view(
        model=Tee,
        context_object_name="tees",
    ), name="golfstats-courses-tees"),

    url(r'^tees/create/$', CreateView.as_view(
        model=Tee,
        success_url=reverse_lazy('golfstats-courses-tees'),
    ), name="golfstats-courses-tee-create"),

    url(r'^tees/(?P<pk>\d+)/$', DetailView.as_view(
        model=Tee,
        context_object_name="tee",
    ), name="golfstats-courses-tee-detail"),

    url(r'^tees/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Tee,
        context_object_name="tee",
        success_url=reverse_lazy('golfstats-courses-tees'),
    ), name="golfstats-courses-tee-detail"),

    url(r'^tees/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Tee,
        context_object_name="tee",
        success_url=reverse_lazy('golfstats-courses-tees'),
    ), name="golfstats-courses-tee-delete"),

    url(r'^holes/$', ListView.as_view(
        model=Hole,
        context_object_name="holes",
    ), name="golfstats-courses-holes"),

    url(r'^holes/create/$', CreateView.as_view(
        model=Hole,
        success_url=reverse_lazy('golfstats-courses-holes'),
    ), name="golfstats-courses-hole-create"),

    url(r'^holes/(?P<pk>\d+)/$', DetailView.as_view(
        model=Hole,
        context_object_name="hole",
    ), name="golfstats-courses-hole-detail"),

    url(r'^holes/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Hole,
        context_object_name="hole",
        success_url=reverse_lazy('golfstats-courses-holes'),
    ), name="golfstats-courses-hole-detail"),

    url(r'^holes/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Hole,
        context_object_name="hole",
        success_url=reverse_lazy('golfstats-courses-holes'),
    ), name="golfstats-courses-hole-delete"),
)
