from django.db import models


from courses.models import Course, CourseHole
from players.models import Player

class Game(models.Model):
    course = models.ForeignKey(Course)
    players = models.ManyToManyField(Player)


class GameHole(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    hole = models.ForeignKey(CourseHole)
    throws = models.IntegerField()
    ob_throws = models.IntegerField()
