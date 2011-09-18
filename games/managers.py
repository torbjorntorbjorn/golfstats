from django.db import models


class GameManager(models.Manager):
    def _get_last_games_generic(self, only_latest, **expr):
        res = self.filter(**expr).order_by('-id')

        if only_latest:
            try:
                return res[0]
            except IndexError:
                pass

        return res

    def get_last_games_by_arena(self, arena, only_latest=False):
        return self._get_last_games_generic(only_latest, course__arena=arena)

    def get_last_games_by_course(self, course, only_latest=False):
        return self._get_last_games_generic(only_latest, course=course)
