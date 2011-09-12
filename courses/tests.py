from django.test import TestCase, Client
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


class ArenaFrontendTest(TestCase):
    def test_create(self):
        c = Client()
        r = c.get("/arenas/create/")

        self.assertContains(r, 'Create or update arena', count=1)

        c = Client()
        r = c.post('/arenas/create/', {
            "name": "Some arena name",
        })

        self.assertEqual(r.status_code, 302)

        self.assertEqual(
            Arena.objects.filter(name="Some arena name").count(), 1)

    def test_index(self):
        arenas = make_arenas(5)

        c = Client()
        r = c.get('/arenas/')

        self.assertEquals(r.status_code, 200)

        context_arenas = r.context_data['arenas']
        for arena in context_arenas:
            self.assertIn(arena, arenas)

    def test_detail(self):
        # Pull up a test arena
        arena = make_arenas()[0]

        c = Client()
        r = c.get("/arenas/%s/" % (arena.id))

        self.assertContains(r, arena.name, count=1)

    def test_delete(self):
        # Pull up a test arena
        arena = make_arenas()[0]

        c = Client()
        r = c.get("/arenas/%s/delete/" % (arena.id))

        self.assertContains(r, arena.name, count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/arenas/%s/delete/" % (arena.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Arena.DoesNotExist,
            Arena.objects.get, id=arena.id)

    def test_update(self):
        # Pull up a test arena
        arena = make_arenas()[0]

        c = Client()
        r = c.get("/arenas/%s/edit/" % (arena.id))

        self.assertContains(r, arena.name, count=1)

        c = Client()
        r = c.post("/arenas/%s/edit/" % (arena.id), {
            "name": "new name",
        })

        self.assertEqual(r.status_code, 302)

        # Ensure that our original and renamed arena
        # have the same IDs
        renamed_arena = Arena.objects.get(name="new name")
        self.assertEqual(renamed_arena.id, arena.id)


class TeeFrontendTest(TestCase):
    def setUp(self):
        self.arena = make_arenas()[0]

    def test_index(self):
        tees = make_tees(self.arena, 5)

        c = Client()
        r = c.get("/tees/")

        self.assertEqual(r.status_code, 200)

        context_tees = r.context_data["tees"]
        for tee in context_tees:
            self.assertIn(tee, tees)

    def test_create(self):
        c = Client()
        r = c.get("/tees/create/")

        self.assertContains(r, 'Create or update tee', count=1)

        c = Client()
        r = c.post('/tees/create/', {
            "arena": self.arena.id,
            "description": "Some kind of tee",
        })

        self.assertEqual(r.status_code, 302)

        self.assertEqual(
            Tee.objects.filter(description="Some kind of tee").count(), 1)

    def test_detail(self):
        tee = make_tees(self.arena)[0]

        c = Client()
        r = c.get("/tees/%s/" % (tee.id))

        self.assertContains(r, tee.description, count=1)

    def test_update(self):
        # Pull up a test arena
        tee = make_tees(self.arena)[0]

        c = Client()
        r = c.get("/tees/%s/edit/" % (tee.id))

        self.assertContains(r, tee.description, count=1)

        c = Client()
        r = c.post("/tees/%s/edit/" % (tee.id), {
            "arena": self.arena.id,
            "description": "new description",
        })

        self.assertEqual(r.status_code, 302)

        # Ensure that our original and renamed arena
        # have the same IDs
        renamed_tee = Tee.objects.get(description="new description")
        self.assertEqual(renamed_tee.id, tee.id)

    def test_delete(self):
        # Pull up a test arena
        tee = make_tees(self.arena)[0]

        c = Client()
        r = c.get("/tees/%s/delete/" % (tee.id))

        self.assertContains(r, tee.description, count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/tees/%s/delete/" % (tee.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Tee.DoesNotExist,
            Tee.objects.get, id=tee.id)


class HoleFrontendTest(TestCase):
    def setUp(self):
        self.arena = make_arenas()[0]
        self.tee = make_tees(self.arena)[0]
        self.basket = make_baskets(self.arena)[0]

    def test_index(self):
        holes = [make_hole(self.tee, self.basket) for x in range(5)]

        c = Client()
        r = c.get("/holes/")

        self.assertEqual(r.status_code, 200)

        context_tees = r.context_data["holes"]
        for hole in context_tees:
            self.assertIn(hole, holes)

    def test_create(self):
        c = Client()
        r = c.get("/holes/create/")

        self.assertContains(r, 'Create or update hole', count=1)

        c = Client()
        r = c.post('/holes/create/', {
            "tee": self.tee.id,
            "basket": self.basket.id,
            "par": "1000",  # Funky test value
        })

        self.assertEqual(r.status_code, 302)

        self.assertEqual(
            Hole.objects.filter(par=1000).count(), 1)

    def test_detail(self):
        hole = make_hole(self.tee, self.basket, 3)

        c = Client()
        r = c.get("/holes/%s/" % (hole.id))

        self.assertContains(r, "Hole %s" % (hole.id), count=1)

    def test_update(self):
        hole = make_hole(self.tee, self.basket, 3)

        c = Client()
        r = c.get("/holes/%s/edit/" % (hole.id))

        self.assertContains(r, "Create or update hole", count=1)

        c = Client()
        r = c.post("/holes/%s/edit/" % (hole.id), {
            "tee": self.tee.id,
            "basket": self.basket.id,
            "par": "1000",  # Funky test value
        })

        self.assertEqual(r.status_code, 302)

        # Ensure that our original and renamed arena
        # have the same IDs
        renamed_hole = Hole.objects.get(par=1000)
        self.assertEqual(renamed_hole.id, hole.id)

    def test_delete(self):
        hole = make_hole(self.tee, self.basket, 3)

        c = Client()
        r = c.get("/holes/%s/delete/" % (hole.id))

        self.assertContains(r, "hole %s" % (hole.id), count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/holes/%s/delete/" % (hole.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Hole.DoesNotExist,
            Hole.objects.get, id=hole.id)


class BasketFrontendTest(TestCase):
    def setUp(self):
        self.arena = make_arenas()[0]

    def test_create(self):
        c = Client()
        r = c.get("/baskets/create/")

        self.assertContains(r, 'Create or update basket', count=1)

        c = Client()
        r = c.post('/baskets/create/', {
            "arena": self.arena.id,
            "description": "Some basket description",
        })

        self.assertEqual(r.status_code, 302)

        self.assertEqual(
            Basket.objects.filter(
                description="Some basket description").count(), 1)

    def test_index(self):
        baskets = make_baskets(self.arena)

        c = Client()
        r = c.get('/baskets/')

        self.assertEquals(r.status_code, 200)

        context_baskets = r.context_data['baskets']
        for basket in context_baskets:
            self.assertIn(basket, baskets)

    def test_detail(self):
        # Pull up a test basket
        basket = make_baskets(self.arena)[0]

        c = Client()
        r = c.get("/baskets/%s/" % (basket.id))

        self.assertContains(r, "Basket %s" % basket.id, count=1)

    def test_delete(self):
        # Pull up a test basket
        basket = make_baskets(self.arena)[0]

        c = Client()
        r = c.get("/baskets/%s/delete/" % (basket.id))

        self.assertContains(r, "Delete basket %s" % basket.id, count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/baskets/%s/delete/" % (basket.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Basket.DoesNotExist,
            Basket.objects.get, id=basket.id)

    def test_update(self):
        # Pull up a test basket
        basket = make_baskets(self.arena)[0]

        c = Client()
        r = c.get("/baskets/%s/edit/" % (basket.id))

        self.assertContains(r, basket.description, count=1)

        c = Client()
        r = c.post("/baskets/%s/edit/" % (basket.id), {
            "arena": self.arena.id,
            "description": "new description",
        })

        self.assertEqual(r.status_code, 302)

        # Ensure that our original and renamed basket
        # have the same IDs
        renamed_basket = Basket.objects.get(
            description="new description")

        self.assertEqual(renamed_basket.id, basket.id)


class CourseFrontendTest(TestCase):
    def setUp(self):
        self.arena = make_arenas()[0]

    def test_index(self):
        courses = make_course(self.arena, 5)

        c = Client()
        r = c.get("/courses/")

        self.assertEqual(r.status_code, 200)

        context_courses = r.context_data["courses"]
        for course in context_courses:
            self.assertIn(course, courses)

    def test_create(self):
        c = Client()
        r = c.get("/courses/create/")

        self.assertContains(r, 'Create or update course', count=1)

        c = Client()
        r = c.post('/courses/create/', {
            "arena": self.arena.id,
            "name": "Some kind of course",
        })

        self.assertEqual(r.status_code, 302)

        self.assertEqual(
            Course.objects.filter(name="Some kind of course").count(), 1)

    def test_detail(self):
        course = make_course(self.arena)[0]

        c = Client()
        r = c.get("/courses/%s/" % (course.id))

        self.assertContains(r, course.name, count=1)

    def test_update(self):
        # Pull up a test arena
        course = make_course(self.arena)[0]

        c = Client()
        r = c.get("/courses/%s/edit/" % (course.id))

        self.assertContains(r, course.name, count=1)

        c = Client()
        r = c.post("/courses/%s/edit/" % (course.id), {
            "arena": self.arena.id,
            "name": "new name",
        })

        self.assertEqual(r.status_code, 302)

        # Ensure that our original and renamed arena
        # have the same IDs
        renamed_course = Course.objects.get(name="new name")
        self.assertEqual(renamed_course.id, course.id)

    def test_delete(self):
        # Make a test course
        course = make_course(self.arena)[0]

        c = Client()
        r = c.get("/courses/%s/delete/" % (course.id))

        self.assertContains(r, course.name, count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/courses/%s/delete/" % (course.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(Course.DoesNotExist,
            Course.objects.get, id=course.id)


class CourseHoleFrontendTest(TestCase):
    def setUp(self):
        self.arena = make_arenas()[0]
        self.course = make_course(self.arena)[0]
        self.tee = make_tees(self.arena)[0]
        self.basket = make_baskets(self.arena)[0]
        self.hole = make_hole(self.tee, self.basket)

    def test_index(self):
        holes = [self.hole for x in range(5)]
        courseholes = make_course_holes(self.course, holes)

        c = Client()
        r = c.get("/courseholes/")

        self.assertEqual(r.status_code, 200)

        context_courseholes = r.context_data["courseholes"]
        for coursehole in context_courseholes:
            self.assertIn(coursehole, courseholes)

    def test_create(self):
        c = Client()
        r = c.get("/courseholes/create/")

        self.assertContains(r, 'Create or update coursehole', count=1)

        c = Client()
        r = c.post('/courseholes/create/', {
            "course": self.course.id,
            "hole": self.hole.id,
            "order": 0,
            "name": "Test coursehole",
        })

        self.assertEqual(r.status_code, 302)

        self.assertEqual(
            CourseHole.objects.filter(name="Test coursehole").count(), 1)

    def test_detail(self):
        coursehole = make_course_holes(self.course, [self.hole])[0]

        c = Client()
        r = c.get("/courseholes/%s/" % (coursehole.id))

        self.assertContains(r, "Coursehole %s" % (coursehole.name), count=1)

    def test_update(self):
        coursehole = make_course_holes(self.course, [self.hole])[0]

        c = Client()
        r = c.get("/courseholes/%s/edit/" % (coursehole.id))

        self.assertContains(r, coursehole.name, count=1)

        c = Client()
        r = c.post("/courseholes/%s/edit/" % (coursehole.id), {
            "course": self.course.id,
            "hole": self.hole.id,
            "order": 0,
            "name": "new name",
        })

        self.assertEqual(r.status_code, 302)

        # Ensure that our original and renamed arena
        # have the same IDs
        renamed_coursehole = CourseHole.objects.get(name="new name")
        self.assertEqual(renamed_coursehole.id, coursehole.id)

    def test_delete(self):
        coursehole = make_course_holes(self.course, [self.hole])[0]

        c = Client()
        r = c.get("/courseholes/%s/delete/" % (coursehole.id))

        self.assertContains(r, coursehole.name, count=1)

        # Simply posting there should delete the instance
        c = Client()
        r = c.post("/courseholes/%s/delete/" % (coursehole.id))

        self.assertEqual(r.status_code, 302)

        # Check that we can't actually load the deleted instance
        self.assertRaises(CourseHole.DoesNotExist,
            CourseHole.objects.get, id=coursehole.id)
