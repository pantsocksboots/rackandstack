from django.template.response import TemplateResponse
from rubric.models import Evolution
from stucon.models import Student
from gradebook.models import ObjectiveScore, TraitScore


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
