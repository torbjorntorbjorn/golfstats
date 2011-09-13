from django import template
from django.template import Variable
from games.models import GameHole

register = template.base.Library()

@register.tag
def get_player_score(parser, token):

    try:
        tag_name, player_id, \
            coursehole_id, game_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires three arguments" %
            token.contents.split()[0])

    return PlayerScoreNode(player_id, coursehole_id, game_id)


class PlayerScoreNode(template.Node):
    def __init__(self, player_id, coursehole_id, game_id):
        self.player_id = Variable(player_id)
        self.coursehole_id = Variable(coursehole_id)
        self.game_id = Variable(game_id)

    def render(self, context):
        super(PlayerScoreNode, self).render(context)
        try:
            gamehole = GameHole.objects.get(
                game__id = self.game_id.resolve(context),
                coursehole__id = self.coursehole_id.resolve(
                    context),
                player__id = self.player_id.resolve(context),
            )
        except GameHole.DoesNotExist:
            return 0
        else:
            return gamehole.throws
