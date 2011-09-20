from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  DeleteView,
                                  UpdateView,)

from courses.models import (Arena,
                            Tee,
                            Hole,
                            Basket,
                            Course,
                            CourseHole,)

from courses.views import (ArenaDetailView,
                            CourseDetailView,)

urlpatterns = patterns('',
    # TODO: Break these out into multiple urlpatterns

    # Arena
    url(r'^arenas/$', ListView.as_view(
        model=Arena,
        context_object_name="arenas",
    ), name="golfstats-courses-arenas"),

    url(r'^arenas/create/$', CreateView.as_view(
        model=Arena,
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-create"),

    url(r'^arenas/(?P<pk>\d+)/$', ArenaDetailView.as_view(
        model=Arena,
        context_object_name="arena",
    ), name="golfstats-courses-arenas-detail"),

    url(r'^arenas/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Arena,
        context_object_name="arena",
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-edit"),

    url(r'^arenas/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Arena,
        context_object_name="arena",
        success_url=reverse_lazy('golfstats-courses-arenas'),
    ), name="golfstats-courses-arenas-delete"),

    # Tees
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
    ), name="golfstats-courses-tee-edit"),

    url(r'^tees/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Tee,
        context_object_name="tee",
        success_url=reverse_lazy('golfstats-courses-tees'),
    ), name="golfstats-courses-tee-delete"),

    # Holes
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
    ), name="golfstats-courses-hole-edit"),

    url(r'^holes/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Hole,
        context_object_name="hole",
        success_url=reverse_lazy('golfstats-courses-holes'),
    ), name="golfstats-courses-hole-delete"),

    # Basket
    url(r'^baskets/$', ListView.as_view(
        model=Basket,
        context_object_name="baskets",
    ), name="golfstats-courses-baskets"),

    url(r'^baskets/create/$', CreateView.as_view(
        model=Basket,
        success_url=reverse_lazy('golfstats-courses-baskets'),
    ), name="golfstats-courses-baskets-create"),

    url('^baskets/(?P<pk>\d+)/$', DetailView.as_view(
        model=Basket,
        context_object_name="basket",
    ), name="golfstats-courses-baskets-detail"),

    url(r'^baskets/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Basket,
        context_object_name="basket",
        success_url=reverse_lazy('golfstats-courses-baskets'),
    ), name="golfstats-courses-baskets-edit"),

    url('^baskets/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Basket,
        context_object_name="basket",
        success_url=reverse_lazy('golfstats-courses-baskets'),
    ), name="golfstats-courses-baskets-delete"),

    # Course
    url(r'^courses/$', ListView.as_view(
        model=Course,
        context_object_name="courses",
    ), name="golfstats-courses-courses"),

    url(r'^courses/create/$', CreateView.as_view(
        model=Course,
        success_url=reverse_lazy('golfstats-courses-courses'),
    ), name="golfstats-courses-course-create"),

    url(r'^courses/(?P<pk>\d+)/$', CourseDetailView.as_view(
        model=Course,
        context_object_name="course",
    ), name="golfstats-courses-course-detail"),

    url(r'^courses/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=Course,
        context_object_name="course",
        success_url=reverse_lazy('golfstats-courses-courses'),
    ), name="golfstats-courses-course-edit"),

    url(r'^courses/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=Course,
        context_object_name="course",
        success_url=reverse_lazy('golfstats-courses-courses'),
    ), name="golfstats-courses-course-delete"),

    # Coursehole
    url(r'^courseholes/$', ListView.as_view(
        model=CourseHole,
        context_object_name="courseholes",
    ), name="golfstats-courses-courseholes"),

    url(r'^courseholes/create/$', CreateView.as_view(
        model=CourseHole,
        success_url=reverse_lazy('golfstats-courses-courseholes'),
    ), name="golfstats-courses-coursehole-create"),

    url(r'^courseholes/(?P<pk>\d+)/$', DetailView.as_view(
        model=CourseHole,
        context_object_name="coursehole",
    ), name="golfstats-courses-coursehole-detail"),

    url(r'^courseholes/(?P<pk>\d+)/edit/', UpdateView.as_view(
        model=CourseHole,
        context_object_name="coursehole",
        success_url=reverse_lazy('golfstats-courses-courseholes'),
    ), name="golfstats-courses-coursehole-edit"),

    url(r'^courseholes/(?P<pk>\d+)/delete/$', DeleteView.as_view(
        model=CourseHole,
        context_object_name="coursehole",
        success_url=reverse_lazy('golfstats-courses-courseholes'),
    ), name="golfstats-courses-coursehole-delete"),
)
