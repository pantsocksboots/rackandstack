from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import (
    BottomFiveResponse,
    NominationResponse,
    PeerFeedbackResponse,
    PerceptionResponse,
    Survey,
    SurveyQuestionResponse,
    TopFiveResponse,
)


class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = [
            "name",
            "survey_qs",
            "nomination_qs",
            "perception_qs",
            "peer_feedback",
            "topbot5",
            "scope",
            "active",
        ]
        labels = {
            "survey_qs": "Survey Questions",
            "nomination_qs": "Nomination Questions",
            "perception_qs": "Perception Questions",
            "topbot5": "Top/Bottom 5",
        }


# https://stackoverflow.com/a/291968
# How to filter the options on a ModelForm object - for example, we don't want to see all students
# in this dropdown, we just want the students who are in the same cohort.
class TopFiveResponseForm(ModelForm):
    class Meta:
        model = TopFiveResponse
        fields = ["top_five_select"]
        labels = {
            "top_five_select": "Top 5 Candidate",
        }


class BottomFiveResponseForm(ModelForm):
    class Meta:
        model = BottomFiveResponse
        fields = ["bottom_five_select"]
        labels = {
            "bottom_five_select": "Bottom 5 Candidate",
        }


class NominationResponseForm(ModelForm):
    class Meta:
        model = NominationResponse
        fields = ["subject", "comment", "question"]
        labels = {
            "subject": "Candidate",
            "comment": "Comment",
        }
        widgets = {"question": forms.HiddenInput()}


class PerceptionResponseForm(ModelForm):
    class Meta:
        model = PerceptionResponse
        fields = ["subject", "score", "question"]
        labels = {
            "score": "Score",
        }
        widgets = {
            "score": forms.RadioSelect(),
            "question": forms.HiddenInput(),
            "subject": forms.HiddenInput(),
        }


class SurveyQuestionResponseForm(ModelForm):
    class Meta:
        model = SurveyQuestionResponse
        fields = ["text", "question"]
        labels = {
            "text": "Answer",
        }
        widgets = {
            "question": forms.HiddenInput(),
        }


class PeerFeedbackResponseForm(ModelForm):
    class Meta:
        model = PeerFeedbackResponse
        fields = ["positive_feedback", "negative_feedback", "subject"]
        widgets = {
            "subject": forms.HiddenInput(),
        }
