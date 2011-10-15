from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(
        template_name="index.html",
    ), name="golfstats-index"),
)

urlpatterns += patterns('',
    url(r'', include('courses.urls')),
    url(r'', include('players.urls')),
    url(r'', include('games.urls')),
    url(r'^api/', include('api.urls')),
    (r'^accounts/',
        include('registration.urls')),
    url(r'^accounts/profile/', direct_to_template, {
        'template': 'registration/profile.html'},
        name='auth_profile'),
)

if settings.DEBUG:
    from frontend.views_debug import login

    urlpatterns += patterns('',
        url(r'^debug/login/$', login, name="golfstats-debug-login"),
    )
