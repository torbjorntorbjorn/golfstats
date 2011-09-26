from datetime import datetime

from django.db import models

from django.contrib.auth.models import User


class Player(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, null=True, blank=True)
    trusts = models.ManyToManyField("Player", null=True, blank=True)
    created = models.DateTimeField()
    pdga_number = models.CharField(max_length=15, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def last_game(self):
        try:
            game = self.game_set.order_by('-created')[0]
            return game
        except IndexError:
            pass

    def does_trust(self, player):
        # Player with no self.user trusts everybody
        if not self.user:
            return True

        # A player trusts himself
        if self.id == player.id:
            return True

        # Try to get the trust relation,
        # or return False if it's not there
        try:
            self.trusts.get(id=player.id)
            return True
        except Player.DoesNotExist:
            return False

    def add_trust(self, player):
        # Both players must have users
        if not self.user or not player.user:
            return False

        # Are we being asked to trust outselves ?
        if self.user.id == player.user.id:
            return

        # Trust new user
        self.trusts.add(player)

    def save(self, *kargs, **kwargs):
        # Set created timestamp if not set
        if not self.created:
            self.created = datetime.now()

        super(Player, self).save(*kargs, **kwargs)
