from django import template
from django.template import Variable
from games.models import GameHole

register = template.base.Library()


@register.tag
def get_gamehole(parser, token):

    try:
        tag_name, player_id, \
            game_id, coursehole_id, \
            context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires four arguments" %
            token.contents.split()[0])

    return PlayerScoreNode(player_id, game_id,
        coursehole_id, context_name)


class PlayerScoreNode(template.Node):
    def __init__(self, player_id, game_id, coursehole_id, context_name):
        self.player_id = Variable(player_id)
        self.game_id = Variable(game_id)
        self.coursehole_id = Variable(coursehole_id)
        self.context_name = context_name

    def render(self, context):
        super(PlayerScoreNode, self).render(context)

        try:
            gamehole = GameHole.objects.get(
                game__id=self.game_id.resolve(context),
                coursehole__id=self.coursehole_id.resolve(
                    context),
                player__id=self.player_id.resolve(context),
            )

            context[self.context_name] = gamehole

        except GameHole.DoesNotExist:
            if self.context_name in context:
                del context[self.context_name]

        return ''
