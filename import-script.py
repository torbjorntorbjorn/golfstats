import os
import stat
import datetime
import requests
import subprocess

from django.core.management import setup_environ
import settings
import MySQLdb
from MySQLdb.cursors import DictCursor
setup_environ(settings)

from courses.models import Course, Arena, Hole, Tee, Basket, CourseHole
from players.models import Player
from games.models import Game, GameHole

OLD_DB_URL = "http://diskgolf.gurgle.no/media/golfstats.sql.gz"
OLD_DB_NAME = "golfstats_import_tmp"
TARGET_FILENAME = OLD_DB_URL.split("/")[-1]  # last part of URL

# Is the file up to date ?
file_current = False
downloaded_file = False

# Check the current file
try:
    target_stat = os.stat(TARGET_FILENAME)
    target_mtime = datetime.datetime.fromtimestamp(
        target_stat[stat.ST_MTIME])
    target_size = target_stat[stat.ST_MTIME]

    # Probably a previous download gone wrong
    if target_size is 0:
        os.unlink(TARGET_FILENAME)
        print "Delete 0-sized download"

    delta = datetime.datetime.now() - target_mtime

    # Too old
    if delta.seconds < 60 * 60 and target_size is not 0:
        print "Database download is fresh, skipping download"
        file_current = True

except OSError:
    target_stat = False

if target_stat and not file_current:
    # Do a HEAD request to check size
    head_req = requests.head(OLD_DB_URL)

    # Same size local and remote ?
    if "content-length" in head_req.headers:
        remote_size = int(head_req.headers["content-length"])

        if remote_size == target_stat[stat.ST_SIZE]:
            print "Database has same size remote and local, assuming same"
            file_current = True

if not file_current:
    get_req = requests.get(OLD_DB_URL)
    get_req.raise_for_status()

    if get_req.ok:
        print "Downloading database"
        with file(TARGET_FILENAME, "wb") as f:
            for content in get_req.iter_content():
                f.write(content)

        downloaded_file = True

    else:
        raise Exception("Could not download database")

if downloaded_file:
    print "Dropping and loading database"
    # Drop database if it exists
    # Assume that the mysql binary can connect without arguments
    p = subprocess.Popen(
        ["mysql", "-e", "DROP DATABASE IF EXISTS `%s`" % (OLD_DB_NAME)])
    p.wait()

    if p.returncode != 0:
        raise Exception("Could not drop database")

    # Create the database anew
    p = subprocess.Popen(
        ["mysql", "-e", "CREATE DATABASE `%s` CHARSET utf8" % (OLD_DB_NAME)])
    p.wait()

    if p.returncode != 0:
        raise Exception("Could not create new database")

    # Load database
    shell_exec = "gunzip -c %s | mysql %s" % (TARGET_FILENAME, OLD_DB_NAME)
    p = subprocess.Popen(shell_exec, shell=True)
    p.wait()

    if p.returncode != 0:
        raise Exception("Could not load database")

# Connect to database using config
db = MySQLdb.connect(
    use_unicode=True, cursorclass=DictCursor,
    db=OLD_DB_NAME, read_default_file="~/.my.cnf")

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
cur.execute('SELECT * FROM `main_player` ORDER BY `id` ASC')
admin_player = Player.objects.create(name='Admin')

for player_row in cur.fetchall():
    player = Player.objects.create(name=player_row['name'])
    players.update({player_row['id']: player})


# Start with going through the different courses
cur.execute('SELECT * FROM `main_track` ORDER BY `id` ASC')

for course_row in cur.fetchall():
    # Now first we must create the Arena
    arena = Arena.objects.create(
       name=course_row['name'])

    # And the Course
    course = Course.objects.create(
        arena=arena, name=course_row['name'])

    # Now go through the holes
    hole_query = """SELECT * FROM `main_hole`
        WHERE `track_id` = %s
        ORDER BY `id` ASC"""
    cur.execute(hole_query, (course_row["id"], ))

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
    game_query = """SELECT * FROM `main_game`
        WHERE `track_id` = %s
        AND `state` = %s
        AND `id`  > 30
        ORDER BY `id` ASC"""
    cur.execute(game_query, (course_row["id"], 2))

    for game_row in cur.fetchall():

        # Time to prepare a new game
        game = Game.objects.create(
            course=course,
            creator=admin_player,
            state=Game.STATE_CREATED,
        )

        # Now find and add players to this game
        game_players = []
        cur.execute("""SELECT * FROM `main_game_players`
            WHERE `game_id` = %s
            ORDER BY `id` ASC""",
            (game_row['id'], ))

        for game_player in cur.fetchall():
            game_players.append(players[game_player['player_id']])

        game.creator = game_players[0]
        game.players = game_players
        game.start()
        game.save()

        # Go through each players score
        cur.execute("""SELECT * FROM `main_game_players`
            WHERE `game_id` = %s
            ORDER BY `id` ASC""",
            (game_row['id'], ))

        for game_player in cur.fetchall():
            score_query = """SELECT * FROM `main_score`
                WHERE `game_id` = %s
                AND `player_id` = %s
                ORDER BY `id` ASC"""

            cur.execute(score_query,
                (game_row["id"], game_player["player_id"]))

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
        game.save()

        print 'Finished game %s (original ID: %s) on %s' % \
            (game.id, game_row['id'], game.course)
