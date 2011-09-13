from django.test import TestCase, Client

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
                coursehole=coursehole,
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

    def test_game_completed(self):
        game = make_game()

        game.start()
        game.save()

        # Check that game without gameholes will not finish
        self.assertRaises(ValidationError, game.finish)

        play_game(game)

        game.finish()
        game.save()

    def test_finished_games_have_been_created(self):
        game = make_game()

        game.start()
        game.save()

        play_game(game)

        game.finish()
        game.save()

        # Check that all players have a FinishedGame
        finished_games = game.finishedgame_set.all()
        finished_games_players = [x.player for x in finished_games]

        players = game.players.all()

        for player in players:
            self.assertIn(player, finished_games_players)

        for finished_game in finished_games:
            courseholes = [h for h in game.gamehole_set.all()
                if h.player == finished_game.player]

            throws = sum([h.throws for h in courseholes])
            self.assertEqual(finished_game.throws, throws)

            score = sum([h.score for h in courseholes])
            self.assertEqual(finished_game.score, score)

            ob_throws = sum([h.ob_throws for h in courseholes])
            self.assertEqual(finished_game.ob_throws, ob_throws)

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

        play_game(game)
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


class GamesFrontendTest(TestCase):
    def test_index(self):
        game = make_game()
        games = [game]

        # Create some more test games
        for i in range(4):
            g = Game.objects.create(
                course=game.course,
            )
            g.player = game.players
            games.append(g)

        c = Client()
        r = c.get("/games/")

        self.assertEqual(r.status_code, 200)

        context_games = r.context_data["games"]
        for game in context_games:
            self.assertIn(game, games)

    def test_create(self):
        # Ensure we have no game
        self.assertEqual(Game.objects.all().count(), 0)

        arena = make_a_whole_arena()
        players = make_players(5)
        course = arena.course_set.all()[0]

        c = Client()
        r = c.get("/games/create/")

        self.assertContains(r, 'Create or update a game', count=1)

        c = Client()
        r = c.post('/games/create/', {
            "course": course.id,
            "players": [p.id for p in players],
            "state": Game.STATE_CREATED,
        })

        self.assertEqual(r.status_code, 302)

        # Ensure we have created a new game
        self.assertEqual(Game.objects.all().count(), 1)

    def test_detail(self):
        game = make_game()

        c = Client()
        r = c.get("/games/%s/" % (game.id))

        self.assertContains(r, "Game %s" % (game.id), count=1)

    def test_delete(self):
        game = make_game()

        c = Client()
        r = c.get("/games/%s/delete/" % (game.id))

        self.assertContains(r, "game %s" % (game.id), count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/games/%s/delete/" % (game.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Game.DoesNotExist,
            Game.objects.get, id=game.id)

    def test_play(self):
        game = make_game()

        c = Client()
        r = c.get("/games/%s/play/" % (game.id))

        self.assertContains(r, "Playing game %s" % (game.id), count=1)

        self.assertEqual(game.state, game.STATE_CREATED)

        c = Client()
        r = c.post("/games/%s/play/" % (game.id), {
            "game-state-change": "button value",
            "wanted-state": "start",
        })

        self.assertEqual(r.status_code, 302)

        # Refresh game
        game = Game.objects.get(id=game.id)

        # Check that game has started
        self.assertEqual(game.state, game.STATE_STARTED)

        # Generate a whole bunch of throws
        throws = {}
        for player in game.players.all():
            for coursehole in game.course.coursehole_set.all():
                score_key = "throws-player:%s-game:%s-coursehole:%s" % (
                    player.id, game.id, coursehole.id)

                ob_score_key = "ob_throws-player:%s-game:%s-coursehole:%s" % (
                    player.id, game.id, coursehole.id)

                throws[score_key] = coursehole.hole.par
                throws[ob_score_key] = 0

        # Submit button key and value
        throws["score"] = "button value"

        c = Client()
        r = c.post("/games/%s/play/" % (game.id), throws)

        # We managed to save scores ?
        self.assertEqual(r.status_code, 302)

        c = Client()
        r = c.post("/games/%s/play/" % (game.id), {
            "game-state-change": "button value",
            "wanted-state": "finish",
        })

        self.assertEqual(r.status_code, 302)

        # Refresh game
        game = Game.objects.get(id=game.id)

        # Check that game has finished
        self.assertEqual(game.state, game.STATE_FINISHED)
