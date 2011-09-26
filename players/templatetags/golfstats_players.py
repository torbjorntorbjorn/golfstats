from django import template
from django.template import Variable
import json


register = template.base.Library()


@register.tag
def player_course_graph(parser, token):

    try:
        tag_name, player, course = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return PlayerCourseGraphNode(player, course)


class PlayerCourseGraphNode(template.Node):
    def __init__(self, player, course):
        self.player = Variable(player)
        self.course = Variable(course)

    def render(self, context):
        super(PlayerCourseGraphNode, self).render(context)
        player = self.player.resolve(context)
        course = self.course.resolve(context)

        # Build a data structure for a players games
        data = {
            'course': course.id,
        }

        results = []

        for game in player.finishedgameplayer_set.filter(
            game__course=course).exclude(dnf=True).order_by('game__started'):
            results.append({
                'score': game.score,
                'game': 'Game %i' % (game.game.id),
            })

        data['results'] = results

        return json.dumps(data)
