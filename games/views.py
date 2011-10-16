import re

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.views.generic import CreateView
from django.shortcuts import render, get_object_or_404

from games.models import Game, GameHole

THROWS_PATTERN = "throws-player:\d+-game:\d+-coursehole:\d+$"
THROWS_RE = re.compile("^" + THROWS_PATTERN)
OB_THROWS_RE = re.compile("^ob_" + THROWS_PATTERN)


# Takes a string containing IDs for
# player, game and coursehole
# Outputs a 3-tuple with the IDs
def _split_pgh(pgh):
    parts = pgh.split("-")

    return [x.split(":")[1] for x in parts[1:]]


def _parse_scores(kv):
    scores = {}

    for key, val in kv:
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

    return scores


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
            scores = _parse_scores(req.POST.items())

            # Iterate through pgh tuples and score dict
            for pgh, throws in scores.items():
                # Realize objects from pgh
                player_id, game_id, coursehole_id = pgh[0], pgh[1], pgh[2]

                # Create gamehole object
                try:
                    gh = GameHole.objects.get(
                        player__id=player_id,
                        game__id=game_id,
                        coursehole__id=coursehole_id)
                except GameHole.DoesNotExist:
                    gh = GameHole()
                    gh.player_id = player_id
                    gh.game_id = game_id
                    gh.coursehole_id = coursehole_id

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


class GameCreateView(CreateView):
    # On success, redirect to game-detail view
    def get_success_url(self):
        return reverse("golfstats-games-games-detail", args=[self.object.id])

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            # Add the current users player as creator
            self.object = form.save(commit=False)
            self.object.creator = request.player
            self.object.save()
            return super(GameCreateView, self).form_valid(form)
        else:
            return self.form_invalid(form)
