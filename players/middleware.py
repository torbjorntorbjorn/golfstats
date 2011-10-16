from players.models import Player


class PlayerMiddleware(object):
    def process_request(self, req):
        # If user is authenticated, put player on request object
        # If there is no player, we create one
        if req.user.is_authenticated() and not hasattr(req, "player"):
            try:
                req.player = req.user.player
            except Player.DoesNotExist:
                # TODO: Present user with view allowing the user to input
                # player name and other player details
                req.player = Player.objects.create(
                    name=req.user.username,
                    user=req.user,
                )
