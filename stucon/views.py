from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.http import QueryDict
from django.template.response import TemplateResponse
from django import template
import csv, io, copy

from .models import Student, Team, Cohort, Source
from .forms import NewStudentUserForm, StudentForm, StudentImageForm
from rubric.models import Trait
from gradebook.models import ObjectiveScore, TraitScore
from surveys.models import (
    TopFiveResponse,
    BottomFiveResponse,
    NominationResponse,
    PerceptionResponse,
)

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def course_admin_check(user):
    return user.groups.filter(name="course_admin").exists()


def student_check(user):
    return user.groups.filter(name="student").exists()


@user_passes_test(course_admin_check)
def create_student_user(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            new_user_form = NewStudentUserForm(request.POST)
            new_user = (
                new_user_form.save()
            )  # Create the User object from the form data.
            st_group = Group.objects.get(name="student")
            st_group.user_set.add(
                new_user
            )  # Add the newly created User to the student group
            st_cohort = Cohort.objects.get(
                pk=student_form["cohort"].value()
            )  # Find the Cohort for adding it to the new student object.
            st_source = Source.objects.get(
                pk=student_form["source"].value()
            )  # Find the Source
            new_student = Student(
                user_id=new_user,
                cohort=st_cohort,
                candidate_number=student_form["candidate_number"].value(),
                source=st_source,
            )
            new_student.save()  # Save the new student to the database.
            messages.add_message(
                request, messages.SUCCESS, f"Successfully created {new_student}."
            )
            return HttpResponseRedirect(reverse("stucon:student_list"))
        else:
            messages.add_message(request, messages.ERROR, student_form.errors)
            return HttpResponseRedirect(reverse("stucon:student_list"))

    user_form = NewStudentUserForm()
    student_form = StudentForm()
    return TemplateResponse(
        request,
        "stucon/student_form.html",
        {"user_form": user_form, "student_form": student_form},
    )


def validate_csv_student_data(csv_file):
    file_is_good = True
    issues = []
    data_set = csv_file.read().decode("UTF-8")
    io_string = io.StringIO(data_set)
    for row in csv.DictReader(io_string):
        candidate_num = row["CN"]
        if Student.objects.filter(candidate_number=candidate_num).exists():
            issues.append(f"Candidate Number already exists: {candidate_num}")
            file_is_good = False
        username = row["username"]
        if User.objects.filter(username=username).exists():
            issues.append(f"Username already exists: {username}")
            file_is_good = False
        source = row["source"]
        cohort = row["cohort"]
        password = row["password"]

        if not Source.objects.filter(name=source).exists():
            issues.append(f"Source does not exist: {source}")
            file_is_good = False
        if not Cohort.objects.filter(name=cohort).exists():
            issues.append(f"Cohort does not exist: {cohort}")
            file_is_good = False

        if len(password) < 8 or password == "12345678" or password == "password":
            issues.append(
                f"Password is: too short; or 12345678; or password. Not allowed."
            )
            file_is_good = False
    return file_is_good, issues


@user_passes_test(course_admin_check)
def bulk_create_students(request):
    if request.method == "GET":
        return TemplateResponse(request, "stucon/bulk_create_students.html", {})

    if request.method == "POST":
        csv_file = request.FILES["file"]
        csv_file_copy = copy.deepcopy(csv_file)

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "This is not a CSV file.")
            return HttpResponseRedirect(reverse("stucon:bulk_create_students"))

        ## VALIDATE THE FILE IS CORRECTLY FORMATTED...
        file_is_good, issues = validate_csv_student_data(csv_file)
        if not file_is_good:
            return TemplateResponse(
                request,
                "stucon/bulk_create_students.html",
                {
                    "file_is_good": file_is_good,
                    "issues": issues,
                },
            )

        ## Open it up and start the import
        if save_csv_student_data(csv_file_copy):
            messages.add_message(
                request, messages.SUCCESS, "Successfully bulk imported users."
            )
        else:
            messages.add_message(request, messages.ERROR, "Issue importing new users.")
        return HttpResponseRedirect(reverse("stucon:bulk_create_students"))


def save_csv_student_data(csv_file):
    data_set = csv_file.read().decode("UTF-8")
    io_string = io.StringIO(data_set)
    for row in csv.DictReader(io_string):
        candidate_num = row["CN"]
        first_name = row["first_name"]
        last_name = row["last_name"]
        username = row["username"]
        password = row["password"]
        source = get_object_or_404(Source.objects.all(), name=row["source"])
        cohort = get_object_or_404(Cohort.objects.all(), name=row["cohort"])
        new_user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        st_group = Group.objects.get(name="student")
        st_group.user_set.add(
            new_user
        )  # Add the newly created User to the student group

        new_student = Student.objects.create(
            user_id=new_user,
            candidate_number=candidate_num,
            cohort=cohort,
            source=source,
        )
        new_student.save()
    return True


@user_passes_test(course_admin_check)
def dump_csv_student_data(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="student_data.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(
        ["CN", "first_name", "last_name", "username", "password", "source", "cohort"]
    )
    students = Student.objects.all()
    for student in students:
        writer.writerow(
            [
                str(student.candidate_number),
                student.user_id.first_name,
                student.user_id.last_name,
                student.username(),
                "hitthesurf",
                str(student.source),
                str(student.cohort),
            ]
        )

    return response


@user_passes_test(course_admin_check)
def student_list(request):
    students = Student.objects.all().order_by("candidate_number")
    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return TemplateResponse(
        request,
        "stucon/student_list.html",
        {
            "page_obj": page_obj,
        },
    )


@user_passes_test(course_admin_check)
def student_edit(request, student_id):
    if request.method == "POST":
        stu = get_object_or_404(Student.objects.all(), pk=student_id)
        student_form = StudentForm(request.POST, instance=stu)
        user_form = NewStudentUserForm(request.POST, instance=stu.user_id)
        user_form.save()
        student_form.save()
        messages.add_message(
            request, messages.SUCCESS, f"Successfully updated { stu }."
        )
        return HttpResponseRedirect(reverse("stucon:student_list"))

    student = get_object_or_404(Student.objects.all(), pk=student_id)
    student_form = StudentForm(instance=student)
    user_form = NewStudentUserForm(instance=student.user_id)

    return TemplateResponse(
        request,
        "stucon/student_form.html",
        {
            "student_form": student_form,
            "user_form": user_form,
            "student": student,
        },
    )


def get_average_traitscore(student_id, trait_id):
    stu = get_object_or_404(Student.objects.all(), pk=student_id)
    tscores = TraitScore.objects.filter(student=student_id, trait=trait_id)
    sum = 0
    count = 0
    for tscore in tscores:
        sum = sum + tscore.score
        count = count + 1
    if count == 0:
        return ("--", count)
    return (round(sum / count, 2), count)


def get_perceptions_avgs(student_id):
    student = get_object_or_404(Student.objects.all(), pk=student_id)
    perceptions = PerceptionResponse.objects.filter(subject=student)
    self_perception = "---"
    others_perception = "---"
    if perceptions.exists():
        self_perception_total = 0
        self_perception_count = 0
        others_perception_total = 0
        others_perception_count = 0
        for perception in perceptions:
            if perception.author == student:
                self_perception_total += perception.score
                self_perception_count += 1
            else:
                others_perception_total += perception.score
                others_perception_count += 1

        if self_perception_count == 0:
            self_perception = "---"
        else:
            self_perception = round(self_perception_total / self_perception_count, 2)

        if others_perception_count == 0:
            others_perception = "---"
        else:
            others_perception = round(
                others_perception_total / others_perception_count, 2
            )

    return {
        "self": self_perception,
        "others": others_perception,
    }


def student_view(request, student_id):
    student = get_object_or_404(Student.objects.all(), pk=student_id)
    trait_averages = {}
    for trait in Trait.objects.all():
        trait_averages[str(trait)] = get_average_traitscore(student_id, trait.id)

    topfive_count = TopFiveResponse.objects.filter(top_five_select=student).count()
    botfive_count = BottomFiveResponse.objects.filter(
        bottom_five_select=student
    ).count()

    perceptions = get_perceptions_avgs(student_id)

    noms = NominationResponse.objects.filter(subject=student)
    pos_noms = 0
    neg_noms = 0
    for nom in noms:
        if nom.question.positive:
            pos_noms += 1
        else:
            neg_noms += 1

    return TemplateResponse(
        request,
        "stucon/student_view.html",
        {
            "student": student,
            "trait_averages": trait_averages,
            "topfive_count": topfive_count,
            "botfive_count": botfive_count,
            "pos_noms": pos_noms,
            "neg_noms": neg_noms,
            "self_perceptions": perceptions["self"],
            "others_perceptions": perceptions["others"],
        },
    )


@user_passes_test(course_admin_check)
def student_delete(request, student_id):
    if request.method == "POST":
        stu = Student.objects.get(pk=student_id)
        stu_name = stu.name()
        stu_user = stu.user_id
        stu_user.delete()  # Delete the User object instead of the Student object - Cascade will delete the Student.
        messages.add_message(
            request, messages.SUCCESS, f"Successfully deleted {stu_name}."
        )
        return HttpResponseRedirect(reverse("stucon:student_list"))
    else:
        student = get_object_or_404(Student.objects.all(), pk=student_id)
        return TemplateResponse(
            request, "stucon/student_delete.html", {"student": student}
        )


@user_passes_test(course_admin_check)
def bulk_edit_list(request):
    student_list = bulk_search(request)
    return TemplateResponse(
        request,
        "stucon/bulk_edit_list.html",
        {
            "students": student_list,
        },
    )


@user_passes_test(course_admin_check)
def bulk_edit_results(request):
    student_list = bulk_search(request)
    return render(
        request,
        "stucon/bulk_edit_results.html",
        {
            "students": student_list,
        },
    )


@user_passes_test(course_admin_check)
def bulk_status_update(request, new_status):
    ids = request.POST.getlist("ids")
    comments = request.POST.getlist("comment")
    if comments == [""]:
        for id in ids:
            stu = get_object_or_404(Student.objects.all(), pk=id)
            if new_status == 0:
                stu.status = "act"
            elif new_status == 1:
                stu.status = "dor"
            elif new_status == 2:
                stu.status = "perf"
            elif new_status == 3:
                stu.status = "med"
            stu.status_comment = ""
            stu.save()
    else:
        for id, comment in zip(ids, comments):
            stu = get_object_or_404(Student.objects.all(), pk=id)
            if new_status == 0:
                stu.status = "act"
            elif new_status == 1:
                stu.status = "dor"
            elif new_status == 2:
                stu.status = "perf"
            elif new_status == 3:
                stu.status = "med"
            stu.status_comment = comment
            stu.save()
    student_list = bulk_search(request)
    return render(
        request,
        "stucon/bulk_edit_results.html",
        {
            "students": student_list,
        },
    )


def status_comment_view_checked(request, student_id):
    stu = get_object_or_404(Student.objects.all(), pk=student_id)
    return render(
        request,
        "stucon/status_comment_form_checked.html",
        {
            "student": stu,
        },
    )


def status_comment_view_unchecked(request, student_id):
    stu = get_object_or_404(Student.objects.all(), pk=student_id)
    return render(
        request,
        "stucon/status_comment_form_unchecked.html",
        {
            "student": stu,
        },
    )


@user_passes_test(course_admin_check)
def bulk_search(request):
    search = request.GET.get("search")
    status = request.GET.get("status")
    sort_by = request.GET.get("sortby")
    list = []
    if search == None and status == None:
        list = Student.objects.all().order_by("user_id__last_name")
        return list

    search = search.lower()
    if status == "all" or status == None:
        students = Student.objects.all()
    else:
        students = Student.objects.filter(status=status)

    for student in students:
        if (
            search in student.name().lower()
            or search in str(student.cohort).lower()
            or search in str(student.source).lower()
            or search in str(student.candidate_number).lower()
        ):
            list.append(student)

    if sort_by == "name":
        sorted_list = sorted(list, key=lambda x: x.name(), reverse=False)
    elif sort_by == "cn":
        sorted_list = sorted(list, key=lambda x: str(x.candidate_number), reverse=False)
    elif sort_by == "cohort":
        sorted_list = sorted(list, key=lambda x: str(x.cohort), reverse=False)
    elif sort_by == "source":
        sorted_list = sorted(list, key=lambda x: str(x.source), reverse=False)
    return sorted_list


@user_passes_test(student_check)
def upload_image(request):
    stu = get_object_or_404(Student.objects.all(), user_id=request.user)
    if request.method == "GET":
        image_form = StudentImageForm(instance=stu)
        return TemplateResponse(
            request,
            "stucon/image_upload.html",
            {
                "image_form": image_form,
            },
        )
    if request.method == "POST":
        image_form = StudentImageForm(request.POST, request.FILES, instance=stu)
        if image_form.is_valid():
            image_form.save()
            messages.add_message(
                request, messages.SUCCESS, "Successfully uploaded a picture."
            )
        else:
            messages.addmessage(request, messages.ERROR, "Picture upload failed.")
        return HttpResponseRedirect(reverse("home:home_page"))


def student_directory(request, cohort):
    student_list = Student.objects.filter(cohort=cohort, status="act")
    cohort = get_object_or_404(Cohort.objects.all(), pk=cohort)
    if Student.objects.filter(user_id=request.user).exists():
        # Our current user is a student
        stu = Student.objects.get(user_id=request.user)
        # Compare the student's cohort to the requested cohort.
        if stu.cohort != cohort:
            # The student is trying to look at a different cohort - redirect and throw an error.
            return HttpResponseRedirect(reverse("home:unauthorized_view"))
    sorted_list = sorted(student_list, key=lambda x: x.name(), reverse=False)
    return TemplateResponse(
        request,
        "stucon/student_directory.html",
        {
            "student_list": sorted_list,
            "cohort": cohort,
        },
    )
