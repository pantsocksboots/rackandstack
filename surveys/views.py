from django.shortcuts import render
from django.template.base import Template
from django.urls import reverse
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import formset_factory
from operator import itemgetter


from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from stucon.models import Student
from .models import (
    Survey,
    NominationResponse,
    PeerFeedbackResponse,
    PerceptionResponse,
    TopFiveResponse,
    BottomFiveResponse,
    SurveyQuestionResponse,
    SurveyQuestion,
)
from .forms import (
    NominationResponseForm,
    SurveyForm,
    TopFiveResponseForm,
    BottomFiveResponseForm,
    PerceptionResponseForm,
    PeerFeedbackResponseForm,
    SurveyQuestionResponseForm,
)


def course_admin_check(user):
    return user.groups.filter(name="course_admin").exists()


def student_check(user):
    if Student.objects.filter(user_id=user.id).exists():
        stu = Student.objects.get(user_id=user.id)

    return user.groups.filter(name="student").exists() and stu.status == "act"


# Create your views here.
@login_required
def survey_list(request):
    if Student.objects.filter(user_id=request.user.id).exists():
        user_is_student = True
    else:
        user_is_student = False
    surveys = Survey.objects.all().order_by("name")
    paginator = Paginator(surveys, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return TemplateResponse(
        request,
        "surveys/survey_list.html",
        {
            "page_obj": page_obj,
            "user_is_student": user_is_student,
        },
    )


@user_passes_test(course_admin_check)
def survey_create(request):
    if request.method == "POST":
        survey_form = SurveyForm(request.POST)
        new_survey = survey_form.save()
        messages.add_message(
            request, messages.SUCCESS, f"Successfully created new survey: {new_survey}."
        )
        return HttpResponseRedirect(reverse("surveys:survey_list"))

    if request.method == "GET":
        survey_form = SurveyForm()
        return TemplateResponse(
            request,
            "surveys/survey_form.html",
            {
                "form": survey_form,
            },
        )


@user_passes_test(course_admin_check)
def survey_view(request, survey_id):
    survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
    return TemplateResponse(request, "surveys/survey_view.html", {"survey": survey})


@user_passes_test(course_admin_check)
def survey_edit(request, survey_id):
    if request.method == "POST":
        survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
        survey_form = SurveyForm(request.POST, instance=survey)
        survey_form.save()
        messages.add_message(
            request, messages.SUCCESS, f"Successfully updated {survey}."
        )
        return HttpResponseRedirect(reverse("surveys:survey_list"))

    if request.method == "GET":
        survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
        edit_form = SurveyForm(instance=survey)
        return TemplateResponse(
            request,
            "surveys/survey_form.html",
            {
                "form": edit_form,
                "survey": survey,
            },
        )


@user_passes_test(course_admin_check)
def survey_delete(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        survey_name = survey.name
        survey.delete()  # Delete the User object instead of the Student object - Cascade will delete the Student.
        messages.add_message(
            request, messages.SUCCESS, f"Successfully deleted {survey_name}."
        )
        return HttpResponseRedirect(reverse("surveys:survey_list"))
    else:
        survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
        return TemplateResponse(
            request, "surveys/survey_delete.html", {"survey": survey}
        )


@user_passes_test(student_check)
def survey_take_menu(request, survey_id):
    stu = get_object_or_404(Student.objects.all(), user_id=request.user.id)
    if request.method == "GET":
        survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
        if survey.active == False:
            messages.add_message(
                request,
                messages.ERROR,
                "The survey you are attempting to take is not active. Please select an active survey.",
            )
            return HttpResponseRedirect(reverse("surveys:survey_list"))
        survey_progress = survey.check_authored_responses_exist(request.user.id)

    return TemplateResponse(
        request,
        "surveys/survey_take_menu.html",
        {
            "survey": survey,
            "survey_progress": survey_progress,
            "cohort": stu.cohort,
        },
    )


@user_passes_test(student_check)
def survey_take_nominations(request, survey_id):
    survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
    student_user = get_object_or_404(Student.objects.all(), user_id=request.user.id)
    nomination_forms = []
    questions = []
    NominationResponseFormset = formset_factory(NominationResponseForm, extra=0)

    if request.method == "POST":
        fs = NominationResponseFormset(request.POST, request.FILES)
        if fs.is_valid():
            for form in fs:
                if NominationResponse.objects.filter(
                    author=student_user,
                    question=form.cleaned_data["question"],
                    survey=survey,
                ).exists():
                    nom_response = NominationResponse.objects.get(
                        author=student_user,
                        question=form.cleaned_data["question"],
                        survey=survey,
                    )
                    nom_response.subject = form.cleaned_data["subject"]
                    nom_response.comment = form.cleaned_data["comment"]
                    nom_response.save()
                else:
                    nom_response = form.save(commit=False)
                    nom_response.author = Student.objects.get(user_id=request.user.id)
                    nom_response.survey = Survey.objects.get(pk=survey_id)
                    nom_response.save()
            messages.add_message(request, messages.SUCCESS, "Nominations saved.")
            return HttpResponseRedirect(
                reverse("surveys:survey_take", kwargs={"survey_id": survey_id})
            )
        else:
            for nomination_q in survey.nomination_qs.all().order_by("question_text"):
                questions.append(nomination_q)
            for form, question in zip(fs, questions):
                if survey.scope == "team":
                    form.fields["subject"].queryset = Student.objects.filter(
                        cohort=student_user.cohort, team=student_user.team, status="act"
                    ).exclude(pk=student_user.pk)
                if survey.scope == "cohort":
                    form.fields["subject"].queryset = Student.objects.filter(
                        cohort=student_user.cohort, status="act"
                    ).exclude(pk=student_user.pk)
                form.question_text = question
            return TemplateResponse(
                request,
                "surveys/survey_take_nominations.html",
                {
                    "survey": survey,
                    "formset": fs,
                },
            )

    for nomination_q in survey.nomination_qs.all().order_by("question_text"):
        questions.append(nomination_q)
        if NominationResponse.objects.filter(
            author=student_user, question=nomination_q, survey=survey
        ).exists():
            nom_resp = NominationResponse.objects.get(
                author=student_user, question=nomination_q, survey=survey
            )
            nomination_forms.append(
                {
                    "subject": nom_resp.subject,
                    "comment": nom_resp.comment,
                    "question": nomination_q,
                }
            )
        else:
            nomination_forms.append(
                {
                    "subject": None,
                    "comment": None,
                    "question": nomination_q,
                }
            )
    fs = NominationResponseFormset(initial=nomination_forms)
    for form, question in zip(fs, questions):
        if survey.scope == "team":
            form.fields["subject"].queryset = Student.objects.filter(
                cohort=student_user.cohort, team=student_user.team
            ).exclude(pk=student_user.pk)
        if survey.scope == "cohort":
            form.fields["subject"].queryset = Student.objects.filter(
                cohort=student_user.cohort
            ).exclude(pk=student_user.pk)
        form.question_text = question
    return TemplateResponse(
        request,
        "surveys/survey_take_nominations.html",
        {
            "survey": survey,
            "formset": fs,
        },
    )


@user_passes_test(student_check)
def survey_take_perceptions(request, survey_id):
    survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
    student_user = get_object_or_404(Student.objects.all(), user_id=request.user.id)
    question_list = []
    teammate_list = []
    perception_forms = []
    PerceptionResponseFormset = formset_factory(PerceptionResponseForm, extra=0)

    if request.method == "POST":
        fs = PerceptionResponseFormset(request.POST, request.FILES)
        if fs.is_valid():
            for form in fs:
                # Save the data
                if PerceptionResponse.objects.filter(
                    author=student_user,
                    subject=form.cleaned_data["subject"],
                    survey=survey,
                    question=form.cleaned_data["question"],
                ).exists():
                    per_resp = PerceptionResponse.objects.get(
                        author=student_user,
                        subject=form.cleaned_data["subject"],
                        survey=survey,
                        question=form.cleaned_data["question"],
                    )
                    per_resp.score = form.cleaned_data["score"]
                    per_resp.save()
                else:
                    per_resp = form.save(commit=False)
                    per_resp.author = student_user
                    per_resp.survey = survey
                    per_resp.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Successfully saved {survey} Perception Scores.",
            )
            return HttpResponseRedirect(
                reverse("surveys:survey_take", kwargs={"survey_id": survey_id})
            )
        else:
            for form in fs:
                question_list.append(form.cleaned_data["question"])
                teammate_list.append(form.cleaned_data["subject"])
            data = zip(question_list, teammate_list, fs)
            return TemplateResponse(
                request,
                "surveys/survey_take_perceptions.html",
                {
                    "survey": survey,
                    "data": data,
                    "formset": fs,
                },
            )

    for perception_q in survey.perception_qs.all().order_by("question_text"):
        teammates = Student.objects.filter(
            team=student_user.team, cohort=student_user.cohort, status="act"
        )
        for teammate in teammates:
            if PerceptionResponse.objects.filter(
                author=student_user,
                subject=teammate,
                question=perception_q,
                survey=survey,
            ).exists():
                perception_resp = PerceptionResponse.objects.get(
                    author=student_user,
                    subject=teammate,
                    question=perception_q,
                    survey=survey,
                )
                perception_forms.append(
                    {
                        "subject": perception_resp.subject,
                        "score": perception_resp.score,
                        "question": perception_q,
                    }
                )
            else:
                perception_forms.append(
                    {
                        "subject": teammate,
                        "score": None,
                        "question": perception_q,
                    }
                )
            question_list.append(perception_q)
            teammate_list.append(teammate)

        fs = PerceptionResponseFormset(initial=perception_forms)
        data = zip(question_list, teammate_list, fs)

    return TemplateResponse(
        request,
        "surveys/survey_take_perceptions.html",
        {
            "survey": survey,
            "data": data,
            "formset": fs,
        },
    )


@user_passes_test(student_check)
def survey_take_topbot5(request, survey_id):
    student_user = get_object_or_404(Student.objects.all(), user_id=request.user.id)
    survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
    TopFiveResponseFormset = formset_factory(TopFiveResponseForm, extra=0)
    BottomFiveResponseFormset = formset_factory(BottomFiveResponseForm, extra=0)

    tf_forms = []
    bf_forms = []

    if request.method == "POST":
        tf_fs = TopFiveResponseFormset(request.POST, request.FILES)
        bf_fs = BottomFiveResponseFormset(request.POST, request.FILES)
        if tf_fs.is_valid():
            tf_selects = []
            for form in tf_fs:
                if form.cleaned_data["top_five_select"] in tf_selects:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "You cannot select the same individual twice for Top 5 or Bottom 5.",
                    )
                    return HttpResponseRedirect(
                        reverse(
                            "surveys:survey_take_topbot5",
                            kwargs={"survey_id": survey_id},
                        )
                    )
                else:
                    tf_selects.append(form.cleaned_data["top_five_select"])
        else:
            for bf_form in bf_fs:
                bf_form.fields["bottom_five_select"].queryset = (
                    Student.objects.filter(cohort=student_user.cohort)
                    .order_by("candidate_number")
                    .exclude(pk=student_user.pk)
                )
            for tf_form in tf_fs:
                tf_form.fields["top_five_select"].queryset = (
                    Student.objects.filter(cohort=student_user.cohort)
                    .order_by("candidate_number")
                    .exclude(pk=student_user.pk)
                )
            return TemplateResponse(
                request,
                "surveys/survey_take_topbot5.html",
                {
                    "survey": survey,
                    "bf_formset": bf_fs,
                    "tf_formset": tf_fs,
                },
            )
        if bf_fs.is_valid():
            bf_selects = []
            for form in bf_fs:
                if form.cleaned_data["bottom_five_select"] in bf_selects:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "You cannot select the same individual twice for Top 5 or Bottom 5.",
                    )
                    return HttpResponseRedirect(
                        reverse(
                            "surveys:survey_take_topbot5",
                            kwargs={"survey_id": survey_id},
                        )
                    )
                else:
                    bf_selects.append(form.cleaned_data["bottom_five_select"])
        else:
            for bf_form in bf_fs:
                bf_form.fields["bottom_five_select"].queryset = (
                    Student.objects.filter(cohort=student_user.cohort)
                    .order_by("candidate_number")
                    .exclude(pk=student_user.pk)
                )
            for tf_form in tf_fs:
                tf_form.fields["top_five_select"].queryset = (
                    Student.objects.filter(cohort=student_user.cohort)
                    .order_by("candidate_number")
                    .exclude(pk=student_user.pk)
                )
            return TemplateResponse(
                request,
                "surveys/survey_take_topbot5.html",
                {
                    "survey": survey,
                    "bf_formset": bf_fs,
                    "tf_formset": tf_fs,
                },
            )

        if tf_fs.is_valid():
            for old_response in TopFiveResponse.objects.filter(
                author=student_user, survey=survey
            ):
                old_response.delete()
            for form in tf_fs:
                tf_response = form.save(commit=False)
                tf_response.author = student_user
                tf_response.survey = survey
                tf_response.save()
        if bf_fs.is_valid():
            for old_response in BottomFiveResponse.objects.filter(
                author=student_user, survey=survey
            ):
                old_response.delete()
            for form in bf_fs:
                bf_response = form.save(commit=False)
                bf_response.author = student_user
                bf_response.survey = survey
                bf_response.save()
        messages.add_message(
            request, messages.SUCCESS, "Successfully saved Top 5 / Bottom 5 Responses."
        )
        return HttpResponseRedirect(
            reverse("surveys:survey_take", kwargs={"survey_id": survey_id})
        )

    if TopFiveResponse.objects.filter(author=student_user, survey=survey).exists():
        tf_responses = TopFiveResponse.objects.filter(
            author=student_user, survey=survey
        )
        for tf_response in tf_responses:
            tf_forms.append(
                {
                    "top_five_select": tf_response.top_five_select,
                }
            )
    else:
        for x in range(0, 5):
            tf_forms.append(
                {
                    "top_five_select": None,
                }
            )
    tf_fs = TopFiveResponseFormset(initial=tf_forms)
    if BottomFiveResponse.objects.filter(author=student_user, survey=survey).exists():
        bf_responses = BottomFiveResponse.objects.filter(
            author=student_user, survey=survey
        )
        for bf_response in bf_responses:
            bf_forms.append(
                {
                    "bottom_five_select": bf_response.bottom_five_select,
                }
            )
    else:
        for x in range(0, 5):
            bf_forms.append(
                {
                    "bottom_five_select": None,
                }
            )
    bf_fs = BottomFiveResponseFormset(initial=bf_forms)

    for bf_form in bf_fs:
        bf_form.fields["bottom_five_select"].queryset = (
            Student.objects.filter(cohort=student_user.cohort)
            .order_by("candidate_number")
            .exclude(pk=student_user.pk)
        )
    for tf_form in tf_fs:
        tf_form.fields["top_five_select"].queryset = (
            Student.objects.filter(cohort=student_user.cohort)
            .order_by("candidate_number")
            .exclude(pk=student_user.pk)
        )

    return TemplateResponse(
        request,
        "surveys/survey_take_topbot5.html",
        {
            "survey": survey,
            "bf_formset": bf_fs,
            "tf_formset": tf_fs,
        },
    )


@user_passes_test(student_check)
def survey_take_pf(request, survey_id):
    student_user = get_object_or_404(Student.objects.all(), user_id=request.user.id)
    survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
    teammates = Student.objects.filter(
        team=student_user.team, cohort=student_user.cohort, status="act"
    )
    PeerFeedbackResponseFormset = formset_factory(PeerFeedbackResponseForm, extra=0)
    pf_forms = []

    if request.method == "POST":
        fs = PeerFeedbackResponseFormset(request.POST, request.FILES)
        if fs.is_valid():
            for form in fs:
                if PeerFeedbackResponse.objects.filter(
                    author=student_user,
                    subject=form.cleaned_data["subject"],
                    survey=survey,
                ).exists():
                    existing_pf = PeerFeedbackResponse.objects.get(
                        author=student_user,
                        subject=form.cleaned_data["subject"],
                        survey=survey,
                    )
                    if (
                        form.cleaned_data["positive_feedback"] == None
                        and form.cleaned_data["negative_feedback"] == None
                    ):
                        existing_pf.delete()
                    else:
                        existing_pf.positive_feedback = form.cleaned_data[
                            "positive_feedback"
                        ]
                        existing_pf.negative_feedback = form.cleaned_data[
                            "negative_feedback"
                        ]
                        existing_pf.save()
                else:
                    new_pf = form.save(commit=False)
                    new_pf.author = student_user
                    new_pf.survey = survey
                    new_pf.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Successfully logged peer feedback responses.",
            )
            return HttpResponseRedirect(
                reverse("surveys:survey_take", kwargs={"survey_id": survey_id})
            )
        else:
            messages.add_message(request, messages.ERROR, "Invalid Form Entry.")
            data = zip(teammates, fs)
            return TemplateResponse(
                request,
                "surveys/survey_take_pf.html",
                {
                    "data": data,
                    "survey": survey,
                    "formset": fs,
                },
            )

    for teammate in teammates:
        if PeerFeedbackResponse.objects.filter(
            author=student_user, subject=teammate, survey=survey
        ).exists():
            existing_pf = PeerFeedbackResponse.objects.get(
                author=student_user, subject=teammate, survey=survey
            )
            pf_forms.append(
                {
                    "subject": existing_pf.subject,
                    "positive_feedback": existing_pf.positive_feedback,
                    "negative_feedback": existing_pf.negative_feedback,
                }
            )
        else:
            pf_forms.append(
                {
                    "subject": teammate,
                    "positive_feedback": None,
                    "negative_feedback": None,
                }
            )
    fs = PeerFeedbackResponseFormset(initial=pf_forms)
    data = zip(teammates, fs)

    return TemplateResponse(
        request,
        "surveys/survey_take_pf.html",
        {
            "data": data,
            "survey": survey,
            "formset": fs,
        },
    )


@user_passes_test(student_check)
def survey_take_qa(request, survey_id):
    survey = get_object_or_404(Survey.objects.all(), pk=survey_id)
    student_user = get_object_or_404(Student.objects.all(), user_id=request.user.id)
    SurveyQuestionResponseFormset = formset_factory(SurveyQuestionResponseForm, extra=0)
    q_forms = []

    if request.method == "POST":
        fs = SurveyQuestionResponseFormset(request.POST, request.FILES)
        if fs.is_valid():
            for form in fs:
                if SurveyQuestionResponse.objects.filter(
                    author=student_user,
                    question=form.cleaned_data["question"],
                    survey=survey,
                ).exists():
                    existing_response = SurveyQuestionResponse.objects.get(
                        author=student_user,
                        question=form.cleaned_data["question"],
                        survey=survey,
                    )
                    if form.cleaned_data["text"] == None:
                        existing_response.delete()
                    else:
                        existing_response.text = form.cleaned_data["text"]
                        existing_response.save()
                else:
                    new_response = form.save(commit=False)
                    new_response.author = student_user
                    new_response.survey = survey
                    new_response.save()
            messages.add_message(
                request, messages.SUCCESS, "Successfully logged Short Answer responses."
            )
            return HttpResponseRedirect(
                reverse("surveys:survey_take", kwargs={"survey_id": survey_id})
            )
        else:
            messages.add_message(request, messages.ERROR, "Invalid Form Entry.")
            data = zip(survey.survey_qs.all(), fs)
            return TemplateResponse(
                request,
                "surveys/survey_take_qa.html",
                {
                    "data": data,
                    "survey": survey,
                    "formset": fs,
                },
            )

    for question in survey.survey_qs.all():
        if SurveyQuestionResponse.objects.filter(
            author=student_user, question=question, survey=survey
        ).exists():
            existing_response = SurveyQuestionResponse.objects.get(
                author=student_user, question=question, survey=survey
            )
            q_forms.append(
                {
                    "text": existing_response.text,
                    "question": question,
                }
            )
        else:
            q_forms.append(
                {
                    "text": None,
                    "question": question,
                }
            )

    fs = SurveyQuestionResponseFormset(initial=q_forms)
    data = zip(survey.survey_qs.all(), fs)

    return TemplateResponse(
        request,
        "surveys/survey_take_qa.html",
        {
            "data": data,
            "formset": fs,
            "survey": survey,
        },
    )


@user_passes_test(course_admin_check)
def survey_review_menu(request):
    return TemplateResponse(request, "surveys/survey_review_menu.html", {})


@user_passes_test(course_admin_check)
def survey_review_nominations(request):
    all_students = Student.objects.filter(status="act")
    data = []
    for student in all_students:
        pos_noms = 0
        neg_noms = 0
        all_noms = NominationResponse.objects.filter(subject=student)
        for nom in all_noms:
            if nom.question.positive:
                pos_noms += 1
            else:
                neg_noms += 1
        data.append(
            {
                "student": student,
                "pos_noms": pos_noms,
                "neg_noms": neg_noms,
            }
        )
    sorted_data = sorted(data, key=itemgetter("pos_noms"), reverse=True)
    return TemplateResponse(
        request,
        "surveys/survey_review_nominations.html",
        {
            "data": sorted_data,
        },
    )


@user_passes_test(course_admin_check)
def survey_review_topbot5(request):
    top5data, bot5data = get_topbot5_data(request)
    return TemplateResponse(
        request,
        "surveys/survey_review_topbot5.html",
        {
            "top5data": top5data,
            "bot5data": bot5data,
        },
    )


def topbot5_search_view(request):
    top5data, bot5data = get_topbot5_data(request)
    return render(
        request,
        "surveys/topbot5_search_results.html",
        {
            "top5data": top5data,
            "bot5data": bot5data,
        },
    )


def get_topbot5_data(request):
    all_students = Student.objects.filter(status="act")
    top5data = []
    bot5data = []
    search = request.GET.get("search")
    if search == None:
        for student in all_students:
            top5count = TopFiveResponse.objects.filter(top_five_select=student).count()
            bot5count = BottomFiveResponse.objects.filter(
                bottom_five_select=student
            ).count()
            top5data.append(
                {
                    "student": student,
                    "top5s": top5count,
                }
            )
            bot5data.append(
                {
                    "student": student,
                    "bot5s": bot5count,
                }
            )
        top5sorted = sorted(top5data, key=itemgetter("top5s"), reverse=True)
        bot5sorted = sorted(bot5data, key=itemgetter("bot5s"), reverse=True)
        return top5sorted, bot5sorted

    search = search.lower()
    for student in all_students:
        if (
            search in student.name().lower()
            or search in str(student.cohort).lower()
            or search in str(student.source).lower()
        ):
            top5count = TopFiveResponse.objects.filter(top_five_select=student).count()
            bot5count = BottomFiveResponse.objects.filter(
                bottom_five_select=student
            ).count()
            top5data.append(
                {
                    "student": student,
                    "top5s": top5count,
                }
            )
            bot5data.append(
                {
                    "student": student,
                    "bot5s": bot5count,
                }
            )
    top5sorted = sorted(top5data, key=itemgetter("top5s"), reverse=True)
    bot5sorted = sorted(bot5data, key=itemgetter("bot5s"), reverse=True)
    return top5sorted, bot5sorted


@user_passes_test(course_admin_check)
def survey_review_questions(request):
    context_questions = search_question_responses(request)
    return TemplateResponse(
        request,
        "surveys/survey_review_questions.html",
        {"questions": context_questions},
    )


def search_question_responses(request):
    all_questions = SurveyQuestion.objects.all()
    context_questions = []

    search = request.GET.get("search")
    if search == None:
        for question in all_questions:
            question_responses = SurveyQuestionResponse.objects.filter(
                question=question
            )
            context_questions.append(
                {
                    "question": question,
                    "responses": question_responses,
                }
            )
        return context_questions
    search = search.lower()

    for question in all_questions:
        question_responses = SurveyQuestionResponse.objects.filter(question=question)
        filtered_response_ids = []
        for response in question_responses:
            if (
                search in str(response.author.name()).lower()
                or search in str(response.text).lower()
                or search in str(response.author.source).lower()
                or search in str(response.author.cohort).lower()
            ):
                filtered_response_ids.append(response.id)
        filtered_responses = SurveyQuestionResponse.objects.filter(
            id__in=filtered_response_ids
        )
        context_questions.append(
            {
                "question": question,
                "responses": filtered_responses,
            }
        )
    return context_questions


@user_passes_test(course_admin_check)
def qa_search_view(request):
    context_questions = search_question_responses(request)
    return render(
        request,
        "surveys/qa_search_results.html",
        {
            "questions": context_questions,
        },
    )


@user_passes_test(course_admin_check)
def nom_search_view(request):
    search = request.GET.get("search")
    sort_by_neg_noms = request.GET.get("negative-sort")
    search = search.lower()
    students = Student.objects.filter(status="act")
    data = []
    for student in students:
        if (
            search in str(student.cohort).lower()
            or search in student.name().lower()
            or search in str(student.source).lower()
        ):
            pos_noms = 0
            neg_noms = 0
            all_noms = NominationResponse.objects.filter(subject=student)
            for nom in all_noms:
                if nom.question.positive:
                    pos_noms += 1
                else:
                    neg_noms += 1
            data.append(
                {
                    "student": student,
                    "pos_noms": pos_noms,
                    "neg_noms": neg_noms,
                }
            )
    if sort_by_neg_noms:
        sorted_data = sorted(data, key=itemgetter("neg_noms"), reverse=True)
    else:
        sorted_data = sorted(data, key=itemgetter("pos_noms"), reverse=True)
    context = {
        "data": sorted_data,
    }
    return render(request, "surveys/nom_search_results.html", context)
