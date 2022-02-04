from django.db import models
from django.contrib.auth.models import User

from stucon.models import Student

from rubric.models import Evolution, Trait
from django.core.exceptions import ValidationError

def is_objective(evo_pk):
    evolution = Evolution.objects.get(pk=evo_pk)
    if evolution.type == 'subj':
        raise ValidationError(f'{evolution} is not an objective evolution.')

# Create your models here.
class TraitScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=False, related_name='trait_student')
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE, null=False)
    evolution = models.ForeignKey(Evolution, on_delete=models.CASCADE, null=False)
    trait_score = models.IntegerChoices('Trait Score', '0 1 2 3 4')
    score = models.PositiveIntegerField(null=False, choices=trait_score.choices)
    grader = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='trait_grader')
    comment = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ["student", "evolution", "trait", "grader"]

    def __str__(self):
        return f"{self.trait} - {self.score} - {self.student} - {self.evolution} - from: {self.grader}"

    def calculate_from_obj_score(self, obj_score):
        pass

class ObjectiveScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False, related_name='obj_student')
    evolution = models.ForeignKey(Evolution, on_delete=models.CASCADE, validators=[is_objective])
    score = models.PositiveIntegerField(null=False)
    grader = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='obj_grader')
    class Meta:
        unique_together = ["student", "evolution"]
    def __str__(self):
        return f"{self.evolution} - {self.score} - {self.student} - from: {self.grader}"
    
    def evolution_type(self):
        return self.evolution.type
    
    def get_time_as_str(self):
        return f"{str(self.score//60).zfill(2)}:{str(self.score%60).zfill(2)}"

