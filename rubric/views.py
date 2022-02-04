from django.http.response import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
import csv, io, copy


from rubric.models import Evolution, ObjectiveEvolution
from rubric.forms import EvolutionForm, ObjectiveEvolutionForm

from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator


# Create your views here.
def course_admin_check(user):
    return user.groups.filter(name='course_admin').exists()

@user_passes_test(course_admin_check)
def evolution_list(request):
    evolutions = Evolution.objects.all().order_by('name')
    paginator = Paginator(evolutions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return TemplateResponse(request, 'rubric/evolution_list.html', {
        'page_obj': page_obj,
    })

@user_passes_test(course_admin_check)
def evolution_create(request):
    if request.method == 'POST':
        form = EvolutionForm(request.POST)
        new_evo = form.save()
        messages.add_message(request, messages.SUCCESS, f"Successfully created {new_evo.name}.")
        return HttpResponseRedirect(reverse('rubric:evolution_list'))

    form = EvolutionForm()
    return TemplateResponse(request, 'rubric/evolution_form.html', { 'form': form })

@user_passes_test(course_admin_check)
def obj_evolution_create(request):
    if request.method == 'POST':
        form = ObjectiveEvolutionForm(request.POST)
        new_evo = form.save()
        messages.add_message(request, messages.SUCCESS, f"Successfully created {new_evo.name}.")
        return HttpResponseRedirect(reverse('rubric:evolution_list'))

    form = ObjectiveEvolutionForm()
    return TemplateResponse(request, 'rubric/evolution_form.html', { 'form': form })

@user_passes_test(course_admin_check)
def evolution_detail(request, evolution_id):
    return TemplateResponse(request, 'rubric/evolution_detail.html', {
        'evolution': get_object_or_404(Evolution.objects.all(), pk=evolution_id)
    })

@user_passes_test(course_admin_check)
def evolution_edit(request, evolution_id):
    if request.method == 'POST':
        evo = get_object_or_404(Evolution.objects.all(), pk=evolution_id)
        if evo.type != 'subj':
            evo = ObjectiveEvolution.objects.get(pk=evolution_id)
            form = ObjectiveEvolutionForm(request.POST, instance=evo)
        else:
            form = EvolutionForm(request.POST, instance=evo)
        form.save()
        messages.add_message(request, messages.SUCCESS, f"Successfully updated { evo.name }.")

    
    if ObjectiveEvolution.objects.filter(pk=evolution_id).exists():
        evolution = ObjectiveEvolution.objects.get(pk=evolution_id)
        form = ObjectiveEvolutionForm(instance=evolution)
    else:
        evolution = Evolution.objects.get(pk=evolution_id)
        form = EvolutionForm(instance=evolution)
    
    return TemplateResponse(request, 'rubric/evolution_form.html', {
        'form': form,
        'evolution': evolution,
    })

@user_passes_test(course_admin_check)
def evolution_delete(request, evolution_id):
    if request.method == 'POST':
        evo = Evolution.objects.get(pk=evolution_id)
        evo_name = evo.name
        evo.delete()
        messages.add_message(request, messages.SUCCESS, f"Successfully deleted {evo_name}.")
        return HttpResponseRedirect(reverse('rubric:evolution_list'))
        # process the deletion.
    else:
        evolution = get_object_or_404(Evolution.objects.all(), pk=evolution_id)
        return TemplateResponse(request, 'rubric/evolution_delete.html', {
            'evolution': evolution
        })

@user_passes_test(course_admin_check)
def evolution_csv_dump(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="evolution_data.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['name','description','traits','type'])
    evolutions = Evolution.objects.all()
    for evolution in evolutions:
        writer.writerow([evolution.name, evolution.description, evolution.traits.all(), str(evolution.type)])

    return response