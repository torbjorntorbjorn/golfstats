from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def last_game(self):
        try:
            game = self.game_set.order_by('-id')[0]
            return game
        except IndexError:
            pass
