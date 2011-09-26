from piston.handler import BaseHandler
from piston.utils import rc

from games.models import Game, GameHole


class GameHandler(BaseHandler):
    allowed_methods = ("GET",)
    model = Game
    fields = ("id", "state", "verified",)
    # TODO: Game JSON is now extremely minimal

    def read(self, req, pk=None):
        base = Game.objects

        if pk is not None:
            return base.get(pk=pk)

        return base.all()


class GameHoleHandler(BaseHandler):
    allowed_methods = ("GET", "PUT",)

    # Custom filtering of gameholes
    # TODO: Is this necessary, can we just use piston ?
    gamehole_fields = (
        'player_id',
        'coursehole_id',
        'throws',
        'ob_throws',
    )

    # Filters according to self.gamehole_fields
    def _filter_gamehole(self, gh):
        # Grab only defined fields
        d = {}
        for name in self.gamehole_fields:
            d[name] = getattr(gh, name)

        return d

    # Return all gameholes for game
    def read(self, req, pk):
        game = Game.objects.get(pk=pk)

        return [self._filter_gamehole(x) for
            x in  game.gamehole_set.all()]

    # Receive gameholes for this game
    # TODO: This doesn't handle removing gamehole
    def update(self, req, pk):
        game = Game.objects.get(pk=pk)

        if req.content_type and req.data:
            for req_gh in req.data:
                # Create or find gamehole object
                try:
                    gh = GameHole.objects.get(
                        player__id=req_gh["player_id"],
                        game__id=game.id,
                        coursehole__id=req_gh["coursehole_id"])
                except GameHole.DoesNotExist:
                    gh = GameHole()
                    gh.player_id = req_gh["player_id"]
                    gh.game_id = game.id
                    gh.coursehole_id = req_gh["coursehole_id"]

                # Set properties and save gamehole
                gh.throws = req_gh["throws"]
                gh.ob_throws = req_gh["ob_throws"]
                gh.save()

            return rc.ALL_OK

        else:
            return rc.BAD_REQUEST
