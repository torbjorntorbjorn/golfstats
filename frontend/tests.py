from django.conf import settings
from django.test import TestCase, Client
from nose.plugins.attrib import attr  # NOQA


class FrontendTest(TestCase):
    def test_index(self):
        c = Client()
        r = c.get("/")

        self.assertContains(r, "Welcome to Golfstats", count=1)


class FrontendDebugTest(TestCase):
    def test_login(self):
        # TODO: Hmf, does this work as expected ?
        old_debug = settings.DEBUG
        settings.DEBUG = True

        c = Client()
        r = c.get("/debug/login/")

        # SessionID cookie has been set ?
        self.assertIn("sessionid", r.cookies.keys())

        # We have been redirected
        self.assertEqual(r.status_code, 302)

        # Restore settings.DEBUG
        settings.DEBUG = old_debug
