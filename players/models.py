from django.db import models

from django.contrib.auth.models import User


class Player(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def last_game(self):
        try:
            game = self.game_set.order_by('-id')[0]
            return game
        except IndexError:
            pass

    def trusts(self, player):
        # Both players must have users
        if not self.user or not player.user:
            return False

        # Our player must have a trust object
        if not self.user.trust:
            return False

        # Can we get the other players user from the
        # users we trust ?
        try:
            self.user.trust.trusts.get(id=player.user.id)
            return True
        except User.DoesNotExist:
            return False


# Represents one user trusting other users
class Trust(models.Model):
    user = models.OneToOneField(User)
    trusts = models.ManyToManyField(User, related_name="trusted_by")
