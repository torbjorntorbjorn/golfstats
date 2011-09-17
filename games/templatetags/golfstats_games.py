from django import template
from django.template import Variable

register = template.base.Library()


@register.tag
def game_player_throws(parser, token):

    try:
        tag_name, game, player = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return GamePlayerThrowsNode(game, player)


class GamePlayerThrowsNode(template.Node):
    def __init__(self, game, player):
        self.game = Variable(game)
        self.player = Variable(player)

    def render(self, context):
        super(GamePlayerThrowsNode, self).render(context)
        game = self.game.resolve(context)
        player = self.player.resolve(context)
        throws = 0

        for gamehole in game.gamehole_set.filter(player=player):
            throws += gamehole.throws

        return throws


@register.tag
def game_player_score(parser, token):

    try:
        tag_name, game, player = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return GamePlayerScoreNode(game, player)


class GamePlayerScoreNode(template.Node):
    def __init__(self, game, player):
        self.game = Variable(game)
        self.player = Variable(player)

    def render(self, context):
        super(GamePlayerScoreNode, self).render(context)
        game = self.game.resolve(context)
        player = self.player.resolve(context)
        score = 0

        for gamehole in game.gamehole_set.filter(player=player):
            score_hole = gamehole.throws - \
                gamehole.coursehole.hole.par

            score += score_hole

        return score


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
