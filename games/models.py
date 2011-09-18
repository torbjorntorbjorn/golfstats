from django.db import models

from django.core.exceptions import ValidationError

from courses.models import Course, CourseHole
from players.models import Player
from games.managers import GameManager


class Game(models.Model):
    STATE_CREATED = 1
    STATE_STARTED = 2
    STATE_FINISHED = 3
    STATE_ABORTED = 4

    STATE_CHOICES = (
        (STATE_CREATED, "Created"),
        (STATE_STARTED, "Started"),
        (STATE_FINISHED, "Finished"),
        (STATE_ABORTED, "Aborted"),
    )

    course = models.ForeignKey(Course)
    creator = models.ForeignKey(Player, related_name="created_games_set")
    players = models.ManyToManyField(Player)
    state = models.PositiveSmallIntegerField(
        choices=STATE_CHOICES, default=STATE_CREATED,
    )

    objects = GameManager()

    def __unicode__(self):
        return "Game %s" % (self.id)

    # Checks that creator is in games
    def _is_creator_in_players(self):
        try:
            self.players.get(id=self.creator.id)
            return True
        except Player.DoesNotExist:
            raise ValidationError(
                "Game creator must be a player in this game")

    def start(self):
        if self.state is not self.STATE_CREATED:
            # TODO: This is bad, we should at least get the state
            # description from STATE_CHOICES
            raise ValidationError("Can only start game when state is '%s'"
                % (self.STATE_CREATED))

        # Check that creator is in players
        self._is_creator_in_players()

        self.state = self.STATE_STARTED

    def finish(self):
        if self.state is not self.STATE_STARTED:
            # TODO: This is bad, we should at least get the state
            # description from STATE_CHOICES
            raise ValidationError("Can only finish game when state is '%s'"
                % (self.STATE_STARTED))

        # Check that creator is in players
        self._is_creator_in_players()

        # We require players in order to finish
        if self.players.count() == 0:
            raise ValidationError("Game must have players to finish")

        # We require some gameholes in order to finish
        if self.gamehole_set.count() == 0:
            raise ValidationError("Holes have not been played in this game")

        # Has the game been completed ?
        if not self._game_completed():
            raise ValidationError(
                "Game is not valid, not all players have played all holes")

        # Generate FinishedGame models
        self._create_finished_games()

        self.state = self.STATE_FINISHED

    def abort(self):
        if self.state is not self.STATE_STARTED:
            # TODO: This is bad, we should at least get the state
            # description from STATE_CHOICES
            raise ValidationError("Can only abort game when state is '%s'"
                % (self.STATE_STARTED))

        self.state = self.STATE_ABORTED

    def _game_completed(self):
        # Will be a map of player and number of holes played
        player_hole_count = {}

        for player in self.players.all():
            # Init the count for all players
            player_hole_count[player] = 0

        for gamehole in self.gamehole_set.all():
            # Is this player in this game ?
            if gamehole.player not in player_hole_count:
                raise ValidationError(
                    "Player %s has played a hole, but is playing this game" % (
                        gamehole.player))

            # Count this hole for this player
            player_hole_count[player] += 1

        # Check that all players have player the correct
        # number of holes
        hole_count = self.course.coursehole_set.count()

        for player, hole_count in player_hole_count.items():
            if hole_count is not hole_count:
                raise ValidationError(
                    "Player %s has not played the correct number of holes" % (
                        player))

        return True

    def _create_finished_games(self):
        # Maps players and FinishedGames
        finished_games = {}

        # Iterate all gameholes
        for gamehole in self.gamehole_set.all():

            # If player hasn't been seen, create a FinishedGame
            if gamehole.player not in finished_games:
                finished_games[gamehole.player] = FinishedGame(
                    player=gamehole.player,
                    game=self,
                    score=0,
                    throws=0,
                    ob_throws=0,
                )

            # Shorthand
            g = finished_games[gamehole.player]

            # Tally up
            g.score += gamehole.score
            g.throws += gamehole.throws
            g.ob_throws += gamehole.ob_throws

        # Save all FinishedGames
        for player, game in finished_games.items():
            game.save()


# This is a de-normalization that will need maintenance,
# but greatly simplifies querying for interesting stuff
class FinishedGame(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)

    score = models.IntegerField()
    throws = models.IntegerField()
    ob_throws = models.IntegerField()


class GameHole(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    coursehole = models.ForeignKey(CourseHole)
    throws = models.IntegerField()
    ob_throws = models.IntegerField()

    class Meta:
        unique_together = ("player", "game", "coursehole")

    @property
    def score(self):
        return self.coursehole.hole.par - self.throws

    def clean(self):
        # Ensure that our course is the same course as
        # the game is played on
        if self.coursehole.course.id != self.game.course.id:
            raise ValidationError(
                "Coursehole must be on same course as game")

    def save(self, *kargs, **kwargs):
        # Trigger custom validation
        self.clean()

        super(GameHole, self).save(*kargs, **kwargs)
