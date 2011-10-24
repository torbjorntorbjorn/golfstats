from players.models import Player


class PlayerMiddleware(object):
    def process_view(self, req, view_func, view_args, view_kwargs):
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
