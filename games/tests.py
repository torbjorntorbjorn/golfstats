import simplejson
from datetime import datetime

from django.test import TestCase
from nose.plugins.attrib import attr  # NOQA

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import User

from games.models import Game, GameHole, Course, CourseHole

from frontend.tests import get_logged_in_client
from courses.tests import make_a_whole_arena, make_course
from players.tests import make_players


def make_game():
    arena = make_a_whole_arena()
    players = make_players(5)

    game = Game.objects.create(
        # TODO: This doesn't look greait
        course=arena.course_set.all()[0],
        creator=players[0],
        created=datetime.now(),
    )
    game.players = players

    return game


def make_finished_game():
    game = make_game()
    game.start()
    game.save()

    play_game(game)
    game.finish()
    game.save()

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
        player = make_players()[0]

        game = Game(
            course=course,
            creator=player,
            created=datetime.now(),
        )
        game.save()
        game.players = [player]

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

        # Check that a FinishedGame got created
        self.assertNotEqual(game.finishedgame.id, None)

        finished_game = game.finishedgame

        # Check that all players have a FinishedGamePlayer
        finished_players = [f.player for f in finished_game.players.all()]
        players = game.players.all()

        # All finishedgame players are in game
        for player in finished_players:
            self.assertIn(player, players)

        # TODO: Figure out how test ordering
        scores = {}

        # Generate our own scores
        for gh in game.gamehole_set.all():
            if gh.player.id not in scores:
                scores[gh.player.id] = {
                    "score": 0,
                    "throws": 0,
                    "ob_throws": 0,
                }

            our_score = scores[gh.player.id]
            our_score["score"] += gh.score
            our_score["throws"] += gh.throws
            our_score["ob_throws"] += gh.ob_throws

        # Check that we have all the scores and correct values
        for fgp in game.finishedgameplayer_set.all():
            our_score = scores[fgp.player.id]

            self.assertEqual(our_score["score"], fgp.score)
            self.assertEqual(our_score["throws"], fgp.throws)
            self.assertEqual(our_score["ob_throws"], fgp.ob_throws)

    def test_finished_game_player_score(self):
        # Make, start and play game
        game = make_game()

        game.start()
        game.save()

        play_game(game)

        # play_game leaves everything at par,
        # so we adjust one gamehole to +1
        choosen_gamehole = game.gamehole_set.all()[0]
        choosen_player = choosen_gamehole.player

        choosen_gamehole.throws = choosen_gamehole.coursehole.hole.par + 1
        choosen_gamehole.save()

        # Finish, trigger creation of finished games
        game.finish()
        game.save()

        # Get the FinishedGamePlayer for choosen_player
        fgp = game.finishedgame.players.get(player__id=choosen_player.id)

        # Assert that we have scored a total of 1
        self.assertEqual(fgp.score, 1)

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

    def test_gamehole_unique_constraint(self):
        game = make_game()
        game.start()
        game.save()

        player = game.players.all()[0]
        coursehole = game.course.coursehole_set.all()[0]

        gh1 = GameHole(
            player=player,
            game=game,
            coursehole=coursehole,
            throws=3,
            ob_throws=0,
        )
        gh1.save()

        # Create identical gamehole as gh1
        gh2 = GameHole(
            player=player,
            game=game,
            coursehole=coursehole,
            throws=3,
            ob_throws=0,
        )

        # Should not be able to save gh2, violates
        # unique constraint.
        self.assertRaises(IntegrityError, gh2.save)

    def test_gamehole_on_wrong_course(self):
        game = make_game()
        game.start()
        game.save()

        player = game.players.all()[0]
        coursehole = game.course.coursehole_set.all()[0]

        gh1 = GameHole(
            player=player,
            game=game,
            coursehole=coursehole,
            throws=3,
            ob_throws=0,
        )
        gh1.save()

        # Create a new course
        course2 = Course.objects.create(
            arena=game.course.arena,
            name="test - course 2",
        )

        # Create a new coursehole
        coursehole2 = CourseHole.objects.create(
            course=course2,
            hole=coursehole.hole,
            order=1,
            name="test - coursehole 2",
        )

        gh2 = GameHole(
            player=player,
            game=game,
            coursehole=coursehole2,
            throws=3,
            ob_throws=0,
        )

        # We shouldn't be able to save gh2,
        # as its coursehole is not the same as the games
        self.assertRaises(ValidationError, gh2.save)

    def test_game_creator_not_in_players(self):
        arena = make_a_whole_arena()
        players = make_players(5)
        extra_player = make_players()[0]

        game = Game.objects.create(
            # TODO: This doesn't look great
            course=arena.course_set.all()[0],
            creator=extra_player,
            created=datetime.now(),
        )
        game.players = players

        # Check that game won't start with invalid creator
        self.assertRaises(ValidationError, game.start)

        # Switch to a valid creator and start game
        game.creator = players[0]
        game.save()
        game.start()
        game.save()

        # Switch back to invalid creator
        game.creator = extra_player
        game.save()

        # Assert that we can't finish game with invalid creator
        self.assertRaises(ValidationError, game.finish)

    def test_verify_game(self):
        # Start, play and finish game
        game = make_game()
        game.start()
        game.save()

        play_game(game)
        game.finish()
        game.save()

        # Have each player verify game
        for player in game.players.all():
            game.add_verification(player)

        self.assertEqual(game.verified, True)

    def test_automatic_verification(self):
        # Create game
        game = make_game()

        # Have all players trust the game creator, they need users
        for player in game.players.all():
            player.user = User.objects.create(
                username="testuser - %s" % (player.name))
            player.save()

            # Use this creator, self.creator is stale
            if player.id == game.creator.id:
                creator = player

            player.add_trust(creator)

        # Refresh games, we have updated players
        game = Game.objects.get(id=game.id)

        # Play and finish game
        game.start()
        game.save()

        play_game(game)
        game.finish()
        game.save()

        # Assert that game has been automatically verified
        self.assertEqual(game.verified, True)

    def test_game_has_dnf_player(self):
        # Create and play game
        game = make_game()
        game.start()
        game.save()
        play_game(game)

        # Grab a gamehole and set to 0
        gh = game.gamehole_set.all()[0]
        gh.throws = 0
        gh.ob_throws = 0
        gh.save()

        # Finish game
        game.finish()

        # Refresh game to get FinishedGame object
        game = Game.objects.get(id=game.id)

        # Grab FinishedGamePlayer we zeroed out a hole for
        fgp = game.finishedgame.players.get(player__id=gh.player.id)

        # Assert that player has DNF state
        self.assertEqual(fgp.dnf, True)


class GamesFrontendTest(TestCase):
    def test_index(self):
        game = make_game()
        games = [game]

        # Create some more test games
        for i in range(4):
            g = Game.objects.create(
                course=game.course,
                creator=game.players.all()[0],
                created=datetime.now(),
            )
            g.player = game.players
            games.append(g)

        c = get_logged_in_client()
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

        c = get_logged_in_client()
        r = c.get("/games/create/")

        self.assertContains(r, 'Create or update a game', count=1)

        c, user = get_logged_in_client(True)

        # Include our auto-generated player in the players of this game
        players.append(user.player)

        # Create the game, our clients player will be the game creator
        r = c.post('/games/create/', {
            "course": course.id,
            "players": [p.id for p in players],
        })

        self.assertEqual(r.status_code, 302)

        # Ensure we have created a new game
        self.assertEqual(Game.objects.all().count(), 1)

        # Get our created game
        game = Game.objects.all()[0]

        # Assert that all posted players are in game
        for player in players:
            self.assertIn(player, game.players.all())

        # Our posted creator is the creator ?
        self.assertEqual(user.player.id, game.creator.id)

    def test_detail(self):
        game = make_game()

        c = get_logged_in_client()
        r = c.get("/games/%s/" % (game.id))

        self.assertContains(r, "Game %s" % (game.id), count=1)

    def test_delete(self):
        game = make_game()

        c = get_logged_in_client()
        r = c.get("/games/%s/delete/" % (game.id))

        self.assertContains(r, "game %s" % (game.id), count=1)

        # Simply posting there should delete the instance
        c = get_logged_in_client()
        r = c.post("/games/%s/delete/" % (game.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Game.DoesNotExist,
            Game.objects.get, id=game.id)

    def test_play(self):
        game = make_game()

        c = get_logged_in_client()
        r = c.get("/games/%s/play/" % (game.id))

        self.assertContains(r, "Playing game %s" % (game.id), count=1)

        self.assertEqual(game.state, game.STATE_CREATED)

        c = get_logged_in_client()
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

        c = get_logged_in_client()
        r = c.post("/games/%s/play/" % (game.id), throws)

        # We managed to save scores ?
        self.assertEqual(r.status_code, 302)

        # Remove the button value from generated scores
        del throws["score"]

        # Iterate over our genetared scores
        # and find them using the ORM
        for key, val in throws.items():
            player_id, game_id, coursehole_id = \
                [k.split(":")[1] for k in key.split("-")[1:]]

            gh = GameHole.objects.get(
                player__id=player_id,
                game__id=game_id,
                coursehole__id=coursehole_id)

            attr_type = key.split("-")[0]

            if attr_type == "throws":
                self.assertEqual(gh.throws, val)

            if attr_type == "ob_throws":
                self.assertEqual(gh.ob_throws, val)

        # Assert we have correct number of GameHoles
        self.assertEqual(len(throws) / 2, GameHole.objects.all().count())

        c = get_logged_in_client()
        r = c.post("/games/%s/play/" % (game.id), {
            "game-state-change": "button value",
            "wanted-state": "finish",
        })

        self.assertEqual(r.status_code, 302)

        # Refresh game
        game = Game.objects.get(id=game.id)

        # Check that game has finished
        self.assertEqual(game.state, game.STATE_FINISHED)


class GamesApiTest(TestCase):
    def test_get_game(self):
        #  Grab an empty response
        c = get_logged_in_client()
        r = c.get("/api/games/")

        # Check response code is reasonable
        self.assertEqual(r.status_code, 200)

        # Should be valid JSON
        res = simplejson.loads(r.content)

        # No players yet, should be empty
        self.assertEqual(res, [])

        # Create two games
        game1 = make_finished_game()
        game2 = make_finished_game()

        # Get list of games
        c = get_logged_in_client()
        r = c.get("/api/games/")

        self.assertEqual(r.status_code, 200)

        resp = simplejson.loads(r.content)

        # Both games in JSON ?
        self.assertEqual(len(resp), 2)

        # Get game ids from JSON response
        resp_ids = [x["id"] for x in resp]

        # Check that both of our games are in there
        self.assertIn(game1.id, resp_ids)
        self.assertIn(game2.id, resp_ids)

        # Get single game
        c = get_logged_in_client()
        r = c.get("/api/games/%s/" % (game1.id))

        self.assertEqual(r.status_code, 200)

        resp = simplejson.loads(r.content)

        # Check that fields hold proper values
        self.assertEqual(game1.id, resp["id"])
        self.assertEqual(game1.state, resp["state"])
        self.assertEqual(game1.verified, resp["verified"])

    def test_get_gameholes(self):
        # Create a finished game
        game = make_finished_game()

        # Grab gameholes JSON
        c = get_logged_in_client()
        r = c.get("/api/games/%s/gameholes/" % (game.id))

        self.assertEqual(r.status_code, 200)

        resp = simplejson.loads(r.content)

        # We have the same amount of gameholes in JSON and db ?
        self.assertEqual(len(resp), len(game.gamehole_set.all()))

        # Check that we can get all our gameholes from JSON
        for resp_gh in resp:
            gh = game.gamehole_set.get(
                player__id=resp_gh["player_id"],
                coursehole__id=resp_gh["coursehole_id"],
                throws=resp_gh["throws"],
                ob_throws=resp_gh["ob_throws"],
            )

            self.assertNotEqual(gh.id, None)

    def test_put_gameholes(self):
        # Create and start game
        game = make_game()
        game.start()
        game.save()

        # Prepare JSON structure, everyone will play par
        gamehole_data = []
        for ch in game.course.coursehole_set.all():
            for player in game.players.all():
                gamehole_data.append({
                    "player_id": player.id,
                    "coursehole_id": ch.id,
                    "throws": ch.hole.par,
                    "ob_throws": 0,
                })

        gamehole_payload = simplejson.dumps(gamehole_data)

        # Check that we have zero gameholes
        self.assertEqual(game.gamehole_set.all().count(), 0)

        # PUT in order to update gameholes
        c = get_logged_in_client()
        r = c.put("/api/games/%s/gameholes/" % (game.id),
            gamehole_payload, content_type="application/json")

        # Response looks good ?
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, "OK")

        # Check that we have created our gameholes
        self.assertEqual(game.gamehole_set.all().count(), len(gamehole_data))

        # Game should be able to finish
        game.finish()
        game.save()

        # Check that game is finished
        self.assertEqual(game.state, game.STATE_FINISHED)
