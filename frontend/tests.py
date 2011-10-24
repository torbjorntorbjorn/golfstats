from django.conf import settings
from django.test import TestCase, Client
from nose.plugins.attrib import attr  # NOQA

from django.contrib.auth.models import User

#from django.conf import settings  # NOQA


def get_logged_in_client(return_user=False):
    # Create a user
    try:
        u = User.objects.get(username="testuser")
    except User.DoesNotExist:
        u = User.objects.create_user("testuser", password="testpassword")

    c = Client()
    # Login to created user
    c.login(username="testuser", password="testpassword")

    if return_user:
        return (c, u)
    return c


class FrontendTest(TestCase):
    def test_index(self):
        c = Client()
        r = c.get("/")

        self.assertContains(r, "Welcome to Golfstats", count=1)


class FrontendMiddleWareLoginRequiredTest(TestCase):
    def test_login_required(self):
        # Assert that we can request a view where auth is not required
        c = Client()
        r = c.get("/")  # View does not require auth

        self.assertEqual(r.status_code, 200)

        # Now we go for a view that requires auth
        c = Client()
        r = c.get("/arenas/create/")  # View requires auth

        # We have received a redirect ?
        self.assertEqual(r.status_code, 302)

        # We have been redirected to LOGIN_URL ?
        self.assertTrue(r["Location"].endswith(settings.LOGIN_URL))

        # Get a logged-in client
        c = get_logged_in_client()

        # Try get view again
        r = c.get("/arenas/create/")  # View requires auth

        # Assert that we can request view now
        self.assertEqual(r.status_code, 200)


#class FrontendDebugTest(TestCase):
#    # TODO: It seems this test only works if it's the first test.
#    # I belive that has something to do with urls.py checking for
#    # settings.DEBUG before including the URL routing for this view.
#    @attr("smalltest")
#    def test_login(self):
#        # TODO: Hmf, does this work as expected ?
#        old_debug = settings.DEBUG
#        settings.DEBUG = True
#
#        c = Client()
#        r = c.get("/debug/login/")
#
#        # SessionID cookie has been set ?
#        self.assertIn("sessionid", r.cookies.keys())
#
#        # We have been redirected
#        self.assertEqual(r.status_code, 302)
#
#        # Restore settings.DEBUG
#        settings.DEBUG = old_debug
