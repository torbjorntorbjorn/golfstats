from django.http import HttpResponseRedirect
from django.core.urlresolvers import resolve
from django.conf import settings


class LoginRequiredMiddleware(object):
    """
    This middleware requires the user to be logged in to acccess
    any view. Exemptions can be made in settings using regex
    matching the URL name of the view.
    """

    def process_view(self, req, view_func, view_args, view_kwargs):
        if not req.user.is_authenticated():
            # Find URL routing, so that we can get at the name
            match = resolve(req.path)

            # Check if the URL routing name is allowed in settings
            for allowed in settings.LOGIN_NOT_REQUIRED_URLS:
                if allowed.match(match.url_name):
                    return  # Continue processing view

            # TODO: This must be removed ASAP
            if settings.DEBUG:
                raise Exception(
                    "URL routing named '%s' requires auth" % (match.url_name))

            # This view requires authentication, so we redirect to login view
            return HttpResponseRedirect(settings.LOGIN_URL)
