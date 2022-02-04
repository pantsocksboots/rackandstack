from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.forms import formset_factory
import csv

from django.urls import reverse
from datetime import datetime, timedelta

from django.contrib import messages

from stucon.models import Cohort, Student
from rubric.models import Evolution, ObjectiveEvolution, Trait

from .forms import (
    SelectEvolutionForm,
    TimeScoreForm,
    TraitScoreForm,
    ObjectiveScoreForm,
)
from .models import ObjectiveScore, TraitScore


def grader_check(user):
    return user.groups.filter(name="grader").exists()

def course_admin_check(user):
    return user.groups.filter(name="course_admin").exists()


# Create your views here.
@user_passes_test(grader_check)
def gradebook_menu(request):
    return TemplateResponse(request, "gradebook/gradebook_menu.html", {})

@user_passes_test(course_admin_check)
def gradebook_csv_dump(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="gradebook_data.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['candidate_number','student','grader','evolution','trait','score', 'comment'])
    traitscores = TraitScore.objects.all()
    for tscore in traitscores:
        writer.writerow([str(tscore.student.candidate_number),str(tscore.student), str(tscore.grader.username), str(tscore.evolution), str(tscore.trait), str(tscore.score), str(tscore.comment)])

    objective_scores = ObjectiveScore.objects.all()
    for oscore in objective_scores:
        writer.writerow([str(oscore.student.candidate_number),str(oscore.student), str(oscore.grader.username), str(oscore.evolution), str(oscore.evolution.traits.all()), str(oscore.score), 'null'])

    return response

@user_passes_test(grader_check)
def grade_evo_list(request, cohort_id, evolution_id):
    students = Student.objects.filter(cohort=cohort_id, status="act").order_by(
        "user_id__last_name"
    )
    cohort = get_object_or_404(Cohort.objects.all(), pk=cohort_id)
    evo = get_object_or_404(Evolution.objects.all(), pk=evolution_id)
    if evo.type != "subj":
        scores = ObjectiveScore.objects.all().filter(evolution=evo)
    else:
        scores = TraitScore.objects.all().filter(grader=request.user, evolution=evo)
    return TemplateResponse(
        request,
        "gradebook/grade_evo_list.html",
        {
            "students": students,
            "evolution": evo,
            "cohort": cohort,
            "scores": scores,
        },
    )


@user_passes_test(grader_check)
def grade_evo(request, student_id, evolution_id):
    evo = get_object_or_404(Evolution, pk=evolution_id)
    stu = get_object_or_404(Student, pk=student_id)
    TraitScoreFormSet = formset_factory(TraitScoreForm, extra=0)
    # HANDLE GET REQUESTS
    if request.method == "GET":
        forms = []
        if evo.type == "subj":
            # Check if the student already has a grade from this user for this evolution.
            data = []
            trait_list = []
            for trait in evo.traits.all():
                if TraitScore.objects.filter(
                    trait=trait,
                    student=student_id,
                    grader=request.user,
                    evolution=evolution_id,
                ).exists():
                    ts = TraitScore.objects.get(
                        trait=trait,
                        student=student_id,
                        grader=request.user,
                        evolution=evolution_id,
                    )
                    data.append(
                        {
                            "trait_score": ts.score,
                            "comment": ts.comment,
                        }
                    )
                else:
                    data.append({"trait_score": "--"})
                trait_list.append(str(trait))

            fs = TraitScoreFormSet(initial=data)
            data = zip(fs, trait_list)
            return TemplateResponse(
                request,
                "gradebook/grade_subj_evo.html",
                {
                    "data": data,
                    "formset": fs,
                    "evolution": evo,
                    "student": stu,
                },
            )

        elif evo.type == "count":
            if ObjectiveScore.objects.filter(
                evolution=evolution_id, student=student_id
            ).exists():
                objscore = ObjectiveScore.objects.get(
                    evolution=evolution_id, student=student_id
                )
                obj_score_form = ObjectiveScoreForm(initial={"score": objscore.score})
            else:
                obj_score_form = ObjectiveScoreForm()
            forms.append(obj_score_form)

        elif evo.type == "time":
            if ObjectiveScore.objects.filter(
                evolution=evolution_id, student=student_id
            ).exists():
                objscore = ObjectiveScore.objects.get(
                    evolution=evolution_id, student=student_id
                )
                time_score_form = TimeScoreForm(
                    initial={"score": timedelta(seconds=objscore.score)}
                )
            else:
                time_score_form = TimeScoreForm(initial={"score": timedelta()})
            forms.append(time_score_form)

        return TemplateResponse(
            request,
            "gradebook/grade_obj_evo.html",
            {
                "forms": forms,
                "evolution": evo,
                "student": stu,
            },
        )
    if request.method == "POST":
        if evo.type == "subj":
            data = request.POST

            fs = TraitScoreFormSet(request.POST, request.FILES)
            if fs.is_valid():
                for form, trait in zip(fs, evo.traits.all()):
                    if form.cleaned_data["trait_score"] == "--":
                        continue
                    if TraitScore.objects.filter(
                        trait=trait,
                        student=student_id,
                        grader=request.user,
                        evolution=evolution_id,
                    ).exists():
                        ts = TraitScore.objects.get(
                            trait=trait,
                            student=student_id,
                            grader=request.user,
                            evolution=evolution_id,
                        )
                        ts.score = form.cleaned_data["trait_score"]
                        ts.comment = form.cleaned_data["comment"]
                    else:
                        ts = TraitScore(
                            trait=trait,
                            student=stu,
                            evolution=evo,
                            grader=request.user,
                            score=form.cleaned_data["trait_score"],
                            comment=form.cleaned_data["comment"],
                        )
                    ts.save()
        elif evo.type == "count":
            if ObjectiveScore.objects.filter(
                student=student_id, evolution=evolution_id
            ).exists():
                os = ObjectiveScore.objects.get(
                    student=student_id, evolution=evolution_id
                )
                os.score = request.POST.get("score")
                os.grader = request.user
            else:
                os = ObjectiveScore(
                    score=request.POST.get("score"),
                    grader=request.user,
                    evolution=evo,
                    student=stu,
                )
            os.save()
        elif evo.type == "time":
            if request.POST.get("score") != "":
                try:
                    time = datetime.strptime(request.POST.get("score"), "%H:%M:%S")
                except:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Invalid input: Time should be formatted HH:MM:SS.",
                    )
                    return HttpResponseRedirect(
                        reverse(
                            "gradebook:grade_evo_list",
                            kwargs={
                                "cohort_id": stu.cohort.id,
                                "evolution_id": evolution_id,
                            },
                        )
                    )
                delta = timedelta(
                    hours=time.hour, minutes=time.minute, seconds=time.second
                )
            if ObjectiveScore.objects.filter(
                student=student_id, evolution=evolution_id
            ).exists():
                os = ObjectiveScore.objects.get(
                    student=student_id, evolution=evolution_id
                )
                os.score = delta.total_seconds()
                os.grader = request.user
            else:
                os = ObjectiveScore(
                    grader=request.user,
                    evolution=evo,
                    student=stu,
                    score=delta.total_seconds(),
                )
            os.save()
    messages.add_message(
        request, messages.SUCCESS, f"Successfully graded {evo} for {stu}."
    )
    return HttpResponseRedirect(
        reverse(
            "gradebook:grade_evo_list",
            kwargs={"cohort_id": stu.cohort.id, "evolution_id": evolution_id},
        )
    )


@user_passes_test(grader_check)
def gradebook_selection(request):
    cohort_id = request.GET.get("cohort_choice")
    evolution_id = request.GET.get("evolution_choice")
    form = SelectEvolutionForm()
    if cohort_id and evolution_id:
        return HttpResponseRedirect(
            reverse(
                "gradebook:grade_evo_list",
                kwargs={"cohort_id": cohort_id, "evolution_id": evolution_id},
            )
        )
    return TemplateResponse(
        request, "gradebook/gradebook_selection.html", {"form": form}
    )


@user_passes_test(grader_check)
def grade_evo_delete(request, student_id, evolution_id):
    evo = get_object_or_404(Evolution, pk=evolution_id)
    stu = get_object_or_404(Student, pk=student_id)

    if request.method == "POST":
        if evo.type == "subj":
            for trait in evo.traits.all():
                if TraitScore.objects.filter(
                    trait=trait,
                    student=student_id,
                    grader=request.user,
                    evolution=evolution_id,
                ).exists():
                    ts = TraitScore.objects.filter(
                        trait=trait,
                        student=student_id,
                        grader=request.user,
                        evolution=evo,
                    )
                    ts.delete()
        else:
            os = get_object_or_404(
                ObjectiveScore, student=student_id, evolution=evolution_id
            )
            os.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            f"Successfully deleted {evo.name} grades for {stu.name()}.",
        )
        return HttpResponseRedirect(
            reverse(
                "gradebook:grade_evo_list",
                kwargs={"cohort_id": stu.cohort.id, "evolution_id": evolution_id},
            )
        )

    if request.method == "GET":
        return TemplateResponse(
            request,
            "gradebook/grade_evo_delete.html",
            {
                "evolution": evo,
                "student": stu,
            },
        )
