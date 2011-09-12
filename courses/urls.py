from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  DeleteView,
                                  UpdateView,)

from courses.models import Arena

urlpatterns = patterns('',
    url(r'^arenas/$', ListView.as_view(
        model=Arena,
        context_object_name="arenas",
    ), name="golfstats-courses-arenas"),

    url(r'^arenas/create/$', CreateView.as_view(
        model=Arena,
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-create"),

    url('^arenas/(?P<pk>\d+)/$', DetailView.as_view(
        model=Arena,
        context_object_name="arena",
    ), name="golfstats-courses-arenas-detail"),

    url('^arenas/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Arena,
        context_object_name="arena",
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-detail"),
)
