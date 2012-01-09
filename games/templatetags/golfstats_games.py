from django import template
from django.template import Variable
from django.template.base import VariableDoesNotExist

from games.models import FinishedGamePlayer, FinishedGame

register = template.base.Library()


@register.tag
def course_best_game(parser, token):

    try:
        tag_name, course, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return CourseBestGameNode(course, context_name)


class CourseBestGameNode(template.Node):
    def __init__(self, course, context_name):
        self.course = Variable(course)
        self.context_name = context_name

    def render(self, context):
        super(CourseBestGameNode, self).render(context)
        course = self.course.resolve(context)

        try:
            context[self.context_name] = FinishedGamePlayer.objects.filter(
                game__course=course).exclude(dnf=True).order_by(
                    'score')[0]
        except IndexError:
            pass

        return ''


@register.tag
def player_games_won(parser, token):

    try:
        tag_name, player = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires one rgument" %
            token.contents.split()[0])

    return PlayerGamesWonNode(player)


class PlayerGamesWonNode(template.Node):
    def __init__(self, player):
        self.player = Variable(player)

    def render(self, context):
        super(PlayerGamesWonNode, self).render(context)
        player = self.player.resolve(context)

        return player.finishedgameplayer_set.filter(
            order=0).count()


@register.tag
def game_winners(parser, token):

    try:
        tag_name, game, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return GameWinnersNode(game, context_name)


class GameWinnersNode(template.Node):
    def __init__(self, game, context_name):
        self.game = Variable(game)
        self.context_name = context_name

    def render(self, context):
        super(GameWinnersNode, self).render(context)
        game = self.game.resolve(context)

        try:
            context[self.context_name] = \
                game.finishedgame.winners
        except FinishedGame.DoesNotExist:
            context[self.context_name] = ''

        return ''


@register.tag
def player_finished_games(parser, token):

    try:
        tag_name, player, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" %
            token.contents.split()[0])

    return PlayerFinishedGamesNode(player, context_name)


class PlayerFinishedGamesNode(template.Node):
    def __init__(self, player, context_name):
        self.player = Variable(player)
        self.context_name = context_name

    def render(self, context):
        super(PlayerFinishedGamesNode, self).render(context)
        player = self.player.resolve(context)

        context[self.context_name] = \
            player.finishedgameplayer_set.order_by('-game__created')

        return ''


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

        # TODO: Should DNF state be handled here ?
        # Check if we have FinishedGamePlayer and DNF,
        # and return string "DNF"
        try:
            fgp = FinishedGamePlayer.objects.get(
                player=player,
                game=game)

            if fgp.dnf:
                return "DNF"
        except FinishedGamePlayer.DoesNotExist:
            pass

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

        # Gamehole might not exist, then we just return the empty string
        try:
            gamehole = self.gamehole.resolve(context)
        except VariableDoesNotExist:
            return ''

        throws = gamehole.throws
        par = gamehole.coursehole.hole.par

        if throws > par:
            return 'overpar'
        elif throws < par:
            return 'belowpar'
        else:
            return 'par'
