from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

DEBUG_USER = "debug_user"
DEBUG_EMAIL = "debug@golfstats"
DEBUG_PASSWORD = "debug_password"


# By posting to this view, a user will be created
# and the requested user will be logged in
# TODO: This function is dangerous and should probably not exist
def login(req):
    if not settings.DEBUG:
        raise Exception("Only enabled in debug mode")

    if not req.user.is_authenticated():
        # Check that user exists and has DEBUG_PASSWORD as password
        try:
            u = User.objects.get(username=DEBUG_USER)
            u.set_password(DEBUG_PASSWORD)

        except User.DoesNotExist:
            User.objects.create_user(DEBUG_USER,
                email=DEBUG_EMAIL, password=DEBUG_PASSWORD)

        # Authenticate and login
        user = authenticate(username=DEBUG_USER, password=DEBUG_PASSWORD)
        auth_login(req, user)

    return HttpResponseRedirect(reverse("golfstats-index"))
