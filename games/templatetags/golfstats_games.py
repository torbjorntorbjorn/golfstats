from django import template
from django.template import Variable

register = template.base.Library()


@register.tag
def get_hole_score_css_class(parser, token):

    try:
        tag_name, gamehole = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires one arguments" %
            token.contents.split()[0])

    return HoleScoreCssClassNode(gamehole)


class HoleScoreCssClassNode(template.Node):
    def __init__(self, gamehole):
        self.gamehole = Variable(gamehole)

    def render(self, context):
        super(HoleScoreCssClassNode, self).render(context)
        gamehole = self.gamehole.resolve(context)
        throws = gamehole.throws
        par = gamehole.coursehole.hole.par

        if throws > par:
            return 'overpar'
        elif throws < par:
            return 'belowpar'
        else:
            return 'par'
