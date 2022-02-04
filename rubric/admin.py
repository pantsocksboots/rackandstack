from django.contrib import admin

from .models import ObjectiveEvolution, Trait, Evolution, ObjectiveEvolution

admin.site.register(Trait)
admin.site.register(Evolution)
admin.site.register(ObjectiveEvolution)