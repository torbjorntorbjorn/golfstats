from django.test import TestCase
from django.core.exceptions import ValidationError

from courses.models import Arena, Tee, Basket, Hole, Course, CourseHole


NUM_HOLES = 18


def make_arenas(count=1):
    arenas = []

    for i in range(0, count):
        c = Arena.objects.create(
            name="Test arena %s" % (i),
        )

        arenas.append(c)
    return arenas


def make_tees(arena, count=1):
    tees = []

    for i in range(0, count):
        t = Tee.objects.create(
            description="Test tee %s" % (i),
            arena=arena,
        )

        tees.append(t)
    return tees


def make_baskets(arena, count=1):
    baskets = []

    for i in range(0, count):
        b = Basket.objects.create(
            arena=arena,
            description="Test basket %s" % (i),
        )

        baskets.append(b)
    return baskets


def make_hole(tee, basket, par=3):
    return Hole.objects.create(
        tee=tee,
        basket=basket,
        par=par,
    )


def make_course(arena, count=1):
    courses = []

    for i in range(0, count):
        c = Course.objects.create(
            arena=arena,
            name="Test course %s" % (i),
        )

        courses.append(c)
    return courses


def make_course_holes(course, holes):
    course_holes = []

    for i, hole in enumerate(holes):
        ch = CourseHole.objects.create(
            course=course,
            hole=hole,
            order=i,
            name="Hole %s on %s" % (i, course.name),
        )

        course_holes.append(ch)
    return course_holes


def make_a_whole_arena():
    arena = make_arenas()[0]

    tees = make_tees(arena, NUM_HOLES)
    baskets = make_baskets(arena, NUM_HOLES)

    holes = []
    for i in range(0, NUM_HOLES):
        hole = make_hole(tees[i], baskets[i])
        holes.append(hole)

    course = make_course(arena)[0]
    make_course_holes(course, holes)

    return arena


class ArenaTest(TestCase):
    def test_courses_basic(self):
        c = make_arenas()[0]

        self.assertNotEqual(c.id, None)

    def test_whole_arena(self):
        arena = make_a_whole_arena()

        courses = arena.course_set.all()
        # Assert that there is exactly one course
        self.assertEqual(len(courses), 1)

        course = courses[0]
        # Assert that there are 18 holes on the course
        holes = course.coursehole_set.all()

        self.assertEqual(len(holes), 18)

    def test_hole_model_validation(self):
        arena1 = make_arenas()[0]
        arena2 = make_arenas()[0]

        tee = make_tees(arena1)[0]
        basket = make_baskets(arena2)[0]

        hole = Hole(
            tee=tee,
            basket=basket,
            par=3,
        )

        self.assertRaises(ValidationError,
            hole.save)

    def test_coursehole_model_validation(self):
        arena1 = make_arenas()[0]
        arena2 = make_arenas()[0]

        tee = make_tees(arena1)[0]
        basket = make_baskets(arena1)[0]

        hole = make_hole(tee, basket)

        course = make_course(arena2)[0]

        coursehole = CourseHole(
            course=course,
            hole=hole,
            order=1,
            name="Test hole",
        )

        self.assertRaises(ValidationError,
            coursehole.save)
