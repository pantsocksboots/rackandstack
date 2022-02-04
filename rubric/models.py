from django.db import models

class Trait(models.Model):

    trait = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.trait

class Evolution(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300, default="")
    traits = models.ManyToManyField(Trait)
    
    class Type(models.TextChoices):
        SUBJECTIVE = 'subj', "Subjective"
        TIMED = 'time', "Timed"
        COUNT = 'count', "Count"
        PASSFAIL = 'pf', "Pass Fail"
    
    type = models.CharField(max_length=12, choices=Type.choices, default=Type.SUBJECTIVE)

    def __str__(self):
        return self.name

class ObjectiveEvolution(Evolution):
    good_score = models.PositiveIntegerField(null=True, blank=True)
    bad_score = models.PositiveIntegerField(null=True, blank=True)

    def is_low_good(self):
        return self.good_score < self.bad_score