from django.test import TestCase


from games.models import Game

from courses.tests import make_arenas, make_course
from players.tests import make_players


class GamesTest(TestCase):
    def test_basic(self):
        arena = make_arenas()[0]
        course = make_course(arena)[0]
        players = make_players(5)

        game = Game.objects.create(
            course=course,
        )
        game.players = players

        self.assertNotEqual(game.id, None)
