from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related
from django.shortcuts import get_object_or_404
from stucon.models import Student
from django.db.models.fields.related import ForeignKey, ManyToManyField


class SurveyQuestion(models.Model):
    question_text = models.CharField(max_length=140, null=False, blank=False)

    def __str__(self):
        return self.question_text


class NominationQuestion(models.Model):
    question_text = models.CharField(max_length=140, null=False, blank=False)
    positive = models.BooleanField()

    def __str__(self):
        return self.question_text


class PerceptionQuestion(models.Model):
    question_text = models.CharField(max_length=140, null=False, blank=False)

    def __str__(self):
        return self.question_text


class Survey(models.Model):
    name = models.CharField(max_length=140, null=False, blank=False)
    survey_qs = models.ManyToManyField(SurveyQuestion)
    perception_qs = models.ManyToManyField(PerceptionQuestion)
    nomination_qs = models.ManyToManyField(NominationQuestion)
    peer_feedback = models.BooleanField(default=True)
    topbot5 = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class SurveyScope(models.TextChoices):
        COHORT = "cohort", "Cohort"
        TEAM = "team", "Team"

    scope = models.CharField(
        max_length=10, choices=SurveyScope.choices, default=SurveyScope.TEAM, null=False
    )

    def __str__(self):
        return self.name

    def get_all_responses(self):
        responses = {}
        # Responses will be stored in a dictionary of lists.
        if self.peer_feedback:
            pf_responses = PeerFeedbackResponse.objects.get(survey=self.pk)
            responses["pf_responses"] = pf_responses

        sur_responses = SurveyQuestionResponse.objects.get(survey=self.pk)
        if len(sur_responses) > 0:
            responses["survey_responses"] = sur_responses

        nom_responses = NominationResponse.objects.get(survey=self.pk)
        if len(nom_responses) > 0:
            responses["nomination_responses"] = nom_responses

        per_responses = PerceptionResponse.objects.get(survey=self.pk)
        if len(per_responses) > 0:
            responses["perception_responses"] = per_responses

        top5_responses = TopFiveResponse.objects.get(survey=self.pk)
        if len(top5_responses) > 0:
            responses["top5_responses"] = top5_responses

        bot5_responses = BottomFiveResponse.objects.get(survey=self.pk)
        if len(bot5_responses) > 0:
            responses["bot5_responses"] = bot5_responses

        return responses

    def check_authored_responses_exist(self, user):
        responses = {}
        stu = get_object_or_404(Student.objects.all(), user_id=user)

        responses["pf_responses"] = PeerFeedbackResponse.objects.filter(
            author=stu, survey=self.pk
        ).exists()
        responses["sur_responses"] = SurveyQuestionResponse.objects.filter(
            author=stu, survey=self.pk
        ).exists()
        responses["nom_responses"] = NominationResponse.objects.filter(
            author=stu, survey=self.pk
        ).exists()
        responses["per_responses"] = PerceptionResponse.objects.filter(
            author=stu, survey=self.pk
        ).exists()
        responses["top5_responses"] = TopFiveResponse.objects.filter(
            author=stu, survey=self.pk
        ).exists()
        responses["bot5_responses"] = BottomFiveResponse.objects.filter(
            author=stu, survey=self.pk
        ).exists()

        return responses


class PeerFeedbackResponse(models.Model):
    author = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="pf_author"
    )
    positive_feedback = models.CharField(max_length=280, null=True, blank=True)
    negative_feedback = models.CharField(max_length=280, null=True, blank=True)
    subject = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="pf_subject"
    )
    current_as_of = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ["author", "subject", "survey"]

    def __str__(self):
        return f"{self.subject} feedback by {self.author} from {self.survey}"


class TopFiveResponse(models.Model):
    author = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="top5_author"
    )
    top_five_select = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    current_as_of = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ["author", "top_five_select", "survey"]

    def __str__(self):
        return f"{self.author} Top Five - {self.current_as_of}"


class BottomFiveResponse(models.Model):
    author = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="bot5_author"
    )
    bottom_five_select = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False
    )
    current_as_of = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ["author", "bottom_five_select", "survey"]

    def __str__(self):
        return f"{self.author} Bottom Five - {self.current_as_of}"


class NominationResponse(models.Model):
    question = models.ForeignKey(NominationQuestion, on_delete=models.CASCADE)
    author = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="nom_author"
    )
    subject = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="nom_subject"
    )
    comment = models.CharField(max_length=280, null=True, blank=True)
    current_as_of = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ["author", "question", "survey"]


class PerceptionResponse(models.Model):
    question = models.ForeignKey(
        PerceptionQuestion,
        on_delete=models.CASCADE,
        null=False,
        related_name="per_question",
    )
    author = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="per_author"
    )
    subject = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=False,
        related_name="per_subject",
        default=-1,
    )

    STRONG_DISAGREE = 0
    DISAGREE = 1
    NEUTRAL = 2
    AGREE = 3
    STRONG_AGREE = 4

    SCORE_CHOICES = (
        (STRONG_DISAGREE, "Strongly Disagree"),
        (DISAGREE, "Disagree"),
        (NEUTRAL, "Neutral"),
        (AGREE, "Agree"),
        (STRONG_AGREE, "Strongly Agree"),
    )
    score = models.PositiveIntegerField(null=False, choices=SCORE_CHOICES)
    current_as_of = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ["author", "subject", "survey", "question"]


class SurveyQuestionResponse(models.Model):
    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        null=False,
        related_name="sur_question",
    )
    author = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=False, related_name="sur_author"
    )
    text = models.CharField(
        max_length=280, null=False, blank=False, default="No comment."
    )
    current_as_of = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ["author", "question", "survey"]
