from piston.handler import BaseHandler

from players.models import Player


class PlayerHandler(BaseHandler):
    allowed_methods = ("GET", )
    model = Player
    fields = ("name", )

    def read(self, request, pk=None):
        base = Player.objects

        if pk is not None:
            return base.get(pk=pk)

        return base.all()
