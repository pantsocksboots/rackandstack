
from django import forms
from gradebook.models import ObjectiveScore, TraitScore
from rubric.models import ObjectiveEvolution, Evolution
from stucon.models import Cohort, Student
from django.forms import ModelForm, ModelChoiceField, CharField, IntegerField, ChoiceField, DurationField
from django.core.validators import MaxValueValidator, MinValueValidator 

class SelectEvolutionForm(forms.Form):
    cohort_choice = ModelChoiceField(Cohort.objects.all())
    evolution_choice = ModelChoiceField(Evolution.objects.all())

SCORE_CHOICES =(
    ("--", "--"),
    (0, "0"),
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
)

class TraitScoreForm(forms.Form):
    label = ''
    trait_score = ChoiceField(choices=SCORE_CHOICES)
    comment = CharField(max_length=200, required=False)

class ObjectiveScoreForm(forms.Form):
    label = ''
    score = IntegerField(min_value=0)

class TimeScoreForm(forms.Form):
    score = DurationField(label="Time")