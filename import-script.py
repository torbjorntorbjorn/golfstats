from django.core.management import setup_environ
import settings
import MySQLdb
from MySQLdb.cursors import DictCursor
setup_environ(settings)

from courses.models import Course, Arena, Hole, Tee, Basket, CourseHole
from players.models import Player
from games.models import Game, GameHole

db = MySQLdb.connect(user='root',
    db='golfstats_import_tmp', passwd='3H4vUDRac7e5WuXa', 
    use_unicode=True, cursorclass=DictCursor)

cur = db.cursor()

Arena.objects.all().delete()
Course.objects.all().delete()
Player.objects.all().delete()
Game.objects.all().delete()
CourseHole.objects.all().delete()
GameHole.objects.all().delete()

courses = []
players = {} 
games = []


# Create the players
cur.execute('SELECT * FROM main_player')
admin_player = Player.objects.create(name='Admin')

for player_row in cur.fetchall():
    player = Player.objects.create(name=player_row['name'])
    players.update({player_row['id']: player})



# Start with going through the different courses 
cur.execute('SELECT * FROM main_track')

for course_row in cur.fetchall():
    # Now first we must create the Arena
    arena = Arena.objects.create(
       name = course_row['name'])

    # And the Course
    course = Course.objects.create(
        arena = arena, name = course_row['name'])

    # Now go through the holes
    cur.execute('SELECT * FROM main_hole WHERE track_id=%i' 
        % course_row['id'])

    holes = cur.fetchall()
    courseholes = {} 

    for hole_row in holes:

        tee = Tee.objects.create(
            arena=arena, description=hole_row['oneline'])

        basket = Basket.objects.create(arena=arena)

        hole = Hole.objects.create(tee=tee,
            basket=basket, par=hole_row['par'])
            
        coursehole = CourseHole.objects.create(
            course=course, hole=hole,
            order=hole_row['order'], name=hole_row['name'])

        courseholes.update({hole_row['id']: coursehole})


    courses.append({
        'id': course_row['id'],
        'course': course,
        'holes': courseholes,
    })

    # Okay, now we have arena with course, baskets, tees and holes
    # Lets try to create some games!
    cur.execute(
        'SELECT * FROM main_game WHERE track_id=%i and state=%i and id > 30'
        % (course_row['id'], 2))

    for game_row in cur.fetchall():

        # Time to prepare a new game
        game = Game.objects.create(
            course=course,
            creator=admin_player,
            state=Game.STATE_CREATED,
        )

        # Now find and add players to this game
        game_players = []
        cur.execute(
            'SELECT * FROM main_game_players WHERE game_id=%s'
            % game_row['id'])

        for game_player in cur.fetchall():
            game_players.append(players[game_player['player_id']])

        game.creator = game_players[0]
        game.players = game_players
        game.start()

        # Go through each players score
        cur.execute(
            'SELECT * FROM main_game_players WHERE game_id=%s'
            % game_row['id'])

        for game_player in cur.fetchall():
            cur.execute(
                'SELECT * FROM main_score WHERE game_id=%s and player_id=%s'
                % (game_row['id'], game_player['player_id']))
            
            for score_row in cur.fetchall():
                # Lets create GameHole
                GameHole.objects.create(
                    game=game,
                    player=players[game_player['player_id']],
                    throws=score_row['throws'],
                    ob_throws=score_row['ob_throws'],
                    coursehole=courseholes[score_row['hole_id']],
                )

        game.finish()

        print 'Finished game on %s' % game.course

