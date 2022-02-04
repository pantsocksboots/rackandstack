import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Survey, SurveyQuestion, SurveyQuestionResponse, PeerFeedbackResponse
from .models import PerceptionQuestion, PerceptionResponse, NominationQuestion, NominationResponse


class SurveyModelTests(TestCase):

    def test_has_name():
        pass