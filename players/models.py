from datetime import datetime

from django.db import models

from django.contrib.auth.models import User

from courses.models import Course


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

    @property
    def played_courses(self, minimum_games=3):
        # TODO: Not happy about this, here we are reaching far too wide.
        # We are coupling too tight with both courses and games,

        # Grab distinct course ids for courses we have played
        all_course_ids = [x["course"] for x in self.game_set.all(). \
            values("course").order_by("course").distinct()]

        valid_course_ids = []

        # Go through all courses we have played,
        # find those where we have more than minimum_games
        for course_id in all_course_ids:
            course_games = self.game_set.filter(course__id=course_id)

            if course_games.count() >= minimum_games:
                valid_course_ids.append(course_id)

        # Realize our valid courses objects
        courses = Course.objects.filter(id__in=valid_course_ids)
        return courses

    @property
    def games_won(self):
        # TODO: Coupling might be a bit tight here as well
        return self.finishedgameplayer_set.filter(
            order=0)

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
