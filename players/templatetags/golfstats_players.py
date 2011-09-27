from django import template
from django.template import Variable
import json

from courses.models import Course
from games.models import Game

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


@register.tag
def player_courses(parser, token):

    try:
        tag_name, player, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return PlayerCoursesNode(player, context_name)


class PlayerCoursesNode(template.Node):
    def __init__(self, player, context_name):
        self.player = Variable(player)
        self.context_name = context_name

    def render(self, context):
        super(PlayerCoursesNode, self).render(context)
        courses = []
        player = self.player.resolve(context)

        # Lets find the courses this player has played on
        for course in Course.objects.all():
            # Try to find games on this course
            games = Game.objects.filter(players__in=[player],
                course=course)

            if games and games.count() > 2:
                courses.append(course)

        context[self.context_name] = courses
        return ''
