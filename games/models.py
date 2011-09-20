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
    verified = models.BooleanField(default=False)

    objects = GameManager()

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return "Game %s" % (self.id)

    def save(self, *kargs, **kwargs):
        super(Game, self).save(*kargs, **kwargs)

        # We are a saved instance, have finished and we are not verified
        # We check the players trust relationship to see if we shall
        # automatically verify the game
        if self.id and self.state == self.STATE_FINISHED and not self.verified:
            # TODO: We shouldn't loop twice here
            for player in self.players.all():
                # Does this player trust the creator ?
                if not player.trusts(self.creator):
                    # This player does not trust the creator,
                    # so we give up here
                    return

            # Add verifications on all players
            for player in self.players.all():
                self.add_verification(player)

            # All players verify the game, let's change state
            self.verify()
            self.save()

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

    # Check that all players have verified this game,
    # and set verified state
    def verify(self):
        # Get all player ids
        player_ids = [x.id for x in self.players.all()]

        # Get the ids of players who have verified this game
        verified_player_ids = [x.player.id for x in
            VerifiedGame.objects.filter(game=self)]

        # Equal amount of of players and verifications ?
        if len(player_ids) != len(verified_player_ids):
            raise ValidationError(
                "Wrong number of verifications")

        # Check that all game players have verified
        for player_id in player_ids:
            if player_id not in verified_player_ids:
                raise ValidationError(
                    "Not all players have verified this game")

        # Set verified state
        self.verified = True

    # Player verifies this game
    def add_verification(self, player):
        VerifiedGame.objects.get_or_create(
            player=player,
            game=self,
        )

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
        # Holds dict with resulting scores for players
        scores = {}

        for gamehole in self.gamehole_set.all():
            # Create scoring dict if we have not seen player
            if gamehole.player not in scores:
                scores[gamehole.player] = {
                    "score": 0,
                    "throws": 0,
                    "ob_throws": 0,
                    "dnf": False,
                }

            # Shorthand
            our_score = scores[gamehole.player]

            # Tally up
            our_score["score"] += gamehole.score
            our_score["throws"] += gamehole.throws
            our_score["ob_throws"] += gamehole.ob_throws

            # Set DNF flag if there are no throws
            if gamehole.throws <= 0:
                our_score["dnf"] = True

        # Sort score objects by score value
        sorted_scores = sorted(list(scores.items()),
            key=lambda s: s[1]["score"])

        finished_game = FinishedGame.objects.create(
            game=self,
        )

        # Create FinishedGamePlayer objects, using
        # ordering based on score objects
        for order, player_score in enumerate(sorted_scores):
            player, score = player_score

            fgp = FinishedGamePlayer.objects.create(
                player=player,
                game=self,
                order=order,
                score=score["score"],
                throws=score["throws"],
                ob_throws=score["ob_throws"],
                dnf=score["dnf"],
            )

            finished_game.players.add(fgp)


# Player has verified that this game is valid
class VerifiedGame(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)

    class Meta:
        unique_together = ("player", "game")

    def save(self, *kargs, **kwargs):
        super(VerifiedGame, self).save(*kargs, **kwargs)

        # If this was the last verification, try to verify the game
        if VerifiedGame.objects.filter(game=self.game).count() == \
            self.game.players.all().count():

            self.game.verify()
            self.game.save()


# This class is a summary of game and gameholes
# It's basically a denormalization, but saves lot of work
class FinishedGamePlayer(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)

    order = models.PositiveIntegerField()
    score = models.IntegerField()
    throws = models.PositiveIntegerField()
    ob_throws = models.PositiveIntegerField()

    dnf = models.BooleanField(default=False)

    class Meta:
        unique_together = ("player", "game", "order")
        ordering = ('order',)


# This class is a summary of game and gameholes
# It's basically a denormalization, but saves lot of work
class FinishedGame(models.Model):
    game = models.OneToOneField(Game)
    players = models.ManyToManyField(FinishedGamePlayer)


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

        if self.game.state != self.game.STATE_STARTED:
            raise ValidationError(
                "GameHole can only be created on a started game")

    def save(self, *kargs, **kwargs):
        # Trigger custom validation
        self.clean()

        super(GameHole, self).save(*kargs, **kwargs)
