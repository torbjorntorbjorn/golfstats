from django.db import models

class GameManager(models.Manager):
    def get_last_game_by_arena(self, arena):
        game = self.filter(
            course__arena=arena).order_by('-id')

        if game:
            return game[0]

        return False

    def get_last_games_by_arena(self, arena):
        return self.filter(
            course__arena=arena).order_by('-id')

    def get_last_game_by_course(self, course):
        game = self.filter(
            course=course).order_by('-id')

        if game:
            return game[0]

        return False

    def get_last_games_by_course(self, course):
        return self.filter(
            course=course).order_by('-id')
