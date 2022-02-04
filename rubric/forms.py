from django.forms import ModelForm
from rubric.models import Evolution, ObjectiveEvolution

class EvolutionForm(ModelForm):
    class Meta:
        model = Evolution
        fields = ['name', 'description', 'traits',]

class ObjectiveEvolutionForm(ModelForm):
    class Meta:
        model = ObjectiveEvolution
        fields = ['name', 'type', 'description', 'traits', 'good_score', 'bad_score',]
    