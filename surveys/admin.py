from django.contrib import admin

# Register your models here.

from .models import BottomFiveResponse, NominationResponse, PeerFeedbackResponse, PerceptionResponse, SurveyQuestion, PerceptionQuestion, NominationQuestion, Survey, SurveyQuestionResponse, TopFiveResponse

admin.site.register(SurveyQuestion)
admin.site.register(PerceptionQuestion)
admin.site.register(NominationQuestion)
admin.site.register(Survey)
admin.site.register(NominationResponse)
admin.site.register(PeerFeedbackResponse)
admin.site.register(TopFiveResponse)
admin.site.register(BottomFiveResponse)
admin.site.register(PerceptionResponse)
admin.site.register(SurveyQuestionResponse)