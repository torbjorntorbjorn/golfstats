from django import template
from django.template import Variable

register = template.base.Library()


@register.tag
def games_list_table(parser, token):

    try:
        tag_name, games = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires one argument" %
            token.contents.split()[0])

    return GamesListNode(games)


class GamesListNode(template.Node):
    def __init__(self, games):
        self.games = Variable(games)

    def render(self, context):
        super(GamesListNode, self).render(context)
        games = self.games.resolve(context)

        t = template.loader.get_template(
            'templatetags/games_list_table.html')

        t_context = template.Context({
            'games': games,
        })

        return t.render(t_context)


@register.tag
def game_standings_table(parser, token):

    try:
        tag_name, game = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires one arguments" %
            token.contents.split()[0])

    return GameStandingsNode(game)


class GameStandingsNode(template.Node):
    def __init__(self, game):
        self.game = Variable(game)

    def render(self, context):
        super(GameStandingsNode, self).render(context)
        game = self.game.resolve(context)

        t = template.loader.get_template(
            'templatetags/game_standings_table.html')

        t_context = template.Context({
            'game': game,
        })

        return t.render(t_context)


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
