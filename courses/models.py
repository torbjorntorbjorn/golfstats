from django.db import models


class Arena(models.Model):
    name = models.CharField(max_length=255)


class Tee(models.Model):
    arena = models.ForeignKey(Arena)
    description = models.CharField(max_length=255)


class Basket(models.Model):
    arena = models.ForeignKey(Arena)
    description = models.CharField(max_length=255)


class Hole(models.Model):
    tee = models.ForeignKey(Tee)
    basket = models.ForeignKey(Basket)
    par = models.IntegerField()


class Course(models.Model):
    arena = models.ForeignKey(Arena)
    name = models.CharField(max_length=255)


class CourseHole(models.Model):
    course = models.ForeignKey(Course)
    hole = models.ForeignKey(Hole)
    order = models.IntegerField()
    name = models.CharField(max_length=255)
