import re

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404

from games.models import Game, GameHole
from courses.models import CourseHole
from players.models import Player

THROWS_PATTERN = "throws-player:\d+-game:\d+-coursehole:\d+$"
THROWS_RE = re.compile("^" + THROWS_PATTERN)
OB_THROWS_RE = re.compile("^ob_" + THROWS_PATTERN)


# Takes a string containing IDs for
# player, game and coursehole
# Outputs a 3-tuple with the IDs
def _split_pgh(pgh):
    parts = pgh.split("-")

    return [x.split(":")[1] for x in parts[1:]]


# Returns a 3-tuple with realized objects
def _get_pgh(p, g, ch):
    return (Player.objects.get(id=p),
        Game.objects.get(id=g),
        CourseHole.objects.get(id=ch))


def play(req, pk):
    game = get_object_or_404(Game, id=pk)

    if req.method == "POST":
        if "game-state-change" in req.POST:
            if not "wanted-state" in req.POST:
                return HttpResponseBadRequest(
                    "Required 'wanted-state' argument")

            wanted_state = req.POST["wanted-state"]
            if not hasattr(game, wanted_state):
                return HttpResponseBadRequest("Unknown wanted state")

            # Run method to change state for game
            state_changer = getattr(game, wanted_state)

            state_changer()
            game.save()

        elif "score" in req.POST:
            # Map between pgh tuple and throws dict
            scores = {}

            for key, val in req.POST.items():
                # Value has to be an integer
                try:
                    score_val = int(val)
                except ValueError:
                    # It wasn't, continue to next one
                    continue

                # Throw registered
                if THROWS_RE.match(key):
                    p, g, ch = _split_pgh(key)

                    score_key = "throws"
                    score_val = val

                # OB throw registered
                elif OB_THROWS_RE.match(key):
                    p, g, ch = _split_pgh(key)

                    score_key = "ob_throws"
                    score_val = val

                # Not a valid score format
                else:
                    continue

                # Create throws dict if not present
                if (p, g, ch) not in scores:
                    scores[(p, g, ch)] = {}

                # Store throw or ob_throw
                scores[(p, g, ch)][score_key] = score_val

            # Iterate through pgh tuples and score dict
            for pgh, throws in scores.items():
                # Realize objects from pgh
                player, game, coursehole = _get_pgh(pgh[0], pgh[1], pgh[2])

                # Create gamehole object
                try:
                    gh = GameHole.objects.get(
                        player=player,
                        game=game,
                        coursehole=coursehole)
                except GameHole.DoesNotExist:
                    gh = GameHole(
                        player=player,
                        game=game,
                        coursehole=coursehole)

                # Set throws if present
                if "throws" in throws:
                    gh.throws = throws["throws"]
                else:
                    gh.throws = 0

                # Set ob throws in present
                if "ob_throws" in throws:
                    gh.ob_throws = throws["ob_throws"]
                else:
                    gh.ob_throws = 0

                gh.save()

        return HttpResponseRedirect(reverse("golfstats-games-games-play",
            args=[game.id]))

    data = {
        "game": game,
    }
    return render(req, "games/game_play.html", data)
