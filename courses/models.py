from django.db import models
from django.core.exceptions import ValidationError


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

    # Custom validation
    def clean(self):
        if self.tee.arena.id != self.basket.arena.id:
            raise ValidationError("Tee and basket not in the same arena")

    def save(self, *kargs, **kwargs):
        # Trigger custom validation
        self.clean()

        super(Hole, self).save(*kargs, **kwargs)


class Course(models.Model):
    arena = models.ForeignKey(Arena)
    name = models.CharField(max_length=255)


class CourseHole(models.Model):
    course = models.ForeignKey(Course)
    hole = models.ForeignKey(Hole)
    order = models.IntegerField()
    name = models.CharField(max_length=255)

    # Custom validation
    def clean(self):
        if self.course.arena.id != self.hole.tee.arena.id:
            raise ValidationError("Course and hole is not in the same arena")

    def save(self, *kargs, **kwargs):
        # Trigger custom validation
        self.clean()

        super(CourseHole, self).save(*kargs, **kwargs)
