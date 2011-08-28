from django.test import TestCase, Client


class FrontendTest(TestCase):
    def test_index(self):
        c = Client()
        r = c.get("/")

        self.assertContains(r, "Welcome to Golfstats", count=1)
