from django.test import TestCase

from django.core.exceptions import ValidationError

from games.models import Game, GameHole

from courses.tests import make_a_whole_arena, make_course
from players.tests import make_players


def make_game():
    arena = make_a_whole_arena()
    players = make_players(5)

    game = Game.objects.create(
        # TODO: This doesn't look greait
        course=arena.course_set.all()[0],
    )
    game.players = players

    return game


def play_game(game):
    players = game.players.all()
    courseholes = game.course.coursehole_set.all()

    # Play all holes for all players
    for coursehole in courseholes:
        for player in players:
            # Play all holes on par
            GameHole.objects.create(
                player=player,
                game=game,
                hole=coursehole,
                throws=coursehole.hole.par,
                ob_throws=0,
            )


class GamesTest(TestCase):
    def test_basic(self):
        game = make_game()
        self.assertNotEqual(game.id, None)

    def test_game_requires_players(self):
        arena = make_a_whole_arena()
        course = make_course(arena)[0]

        game = Game(
            course=course,
        )
        game.save()

        game.start()

        # Check that game doesn't finish without players
        self.assertRaises(ValidationError, game.finish)

    def test_game_start(self):
        game = make_game()

        # Game starts out created
        self.assertEqual(game.state, game.STATE_CREATED)

        # Start game
        game.start()
        game.save()

        # Check that game is started
        self.assertEqual(game.state, game.STATE_STARTED)

        # Check that game can not be started again
        self.assertRaises(ValidationError, game.start)

    def test_game_finish(self):
        game = make_game()
        game.start()
        game.save()

        # Check that game is started
        self.assertEqual(game.state, game.STATE_STARTED)

        game.finish()
        game.save()

        # Check that game is finished
        self.assertEqual(game.state, game.STATE_FINISHED)

        # Check that game can not be finished again
        self.assertRaises(ValidationError, game.finish)

        # Check that game can not be started again
        self.assertRaises(ValidationError, game.start)

    def test_game_abort(self):
        game = make_game()
        game.start()
        game.save()

        # Check that game is started
        self.assertEqual(game.state, game.STATE_STARTED)

        game.abort()
        game.save()

        # Check that game is aborted
        self.assertEqual(game.state, game.STATE_ABORTED)

        # Check that game can not be aborted again
        self.assertRaises(ValidationError, game.abort)

        # Check that game can not be started again
        self.assertRaises(ValidationError, game.start)
