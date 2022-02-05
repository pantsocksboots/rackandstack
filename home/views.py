from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from rubric.models import Evolution
from stucon.models import Student
from gradebook.models import ObjectiveScore, TraitScore
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse



def home_view(request):
    evos = Evolution.objects.all().count()
    students = Student.objects.all().count()
    scores = ObjectiveScore.objects.all().count() + TraitScore.objects.all().count()
    user_is_student = request.user.groups.filter(name="student").exists()
    user_is_grader = request.user.groups.filter(name="grader").exists()
    user_is_course_admin = request.user.groups.filter(name="course_admin").exists()

    return TemplateResponse(
        request,
        "home/main.html",
        {
            "num_evos": evos,
            "num_students": students,
            "num_scores": scores,
            "user_is_student": user_is_student,
            "user_is_grader": user_is_grader,
            "user_is_course_admin": user_is_course_admin,
        },
    )


def unauthorized_view(request):
    return TemplateResponse(
        request,
        "home/unauthorized.html",
        {},
    )

def reset_password(request):
    if request.method == "GET":
        pw_change_form = PasswordChangeForm(user=request.user)
        return TemplateResponse(request, "home/password_reset.html",{
            "pw_change_form": pw_change_form,
        })
    if request.method == "POST":
        pw_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        if pw_change_form.is_valid():
            pw_change_form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully changed password.")
        else:
            print(pw_change_form.error_messages)
            messages.add_message(request, messages.ERROR, "Error: Password not changed successfully.")
        return HttpResponseRedirect(reverse("home:home_page"))