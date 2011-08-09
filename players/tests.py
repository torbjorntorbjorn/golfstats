from django.test import TestCase

from players.models import Player


def make_players(count = 1):
    players = []

    for i in range(0, count):
        p = Player.objects.create(
            name = "Test player %s" % (i),
        )

        players.append(p)

    return players

class PlayerTest(TestCase):
    def test_basic_player(self):
        p = make_players()[0]

        self.assertNotEqual(p.id, None)
