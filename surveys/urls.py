from django.urls import path, reverse_lazy
from . import views

app_name = 'surveys'
urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('create', views.survey_create, name='survey_create'),
    path('<int:survey_id>/edit', views.survey_edit, name='survey_edit'),
    path('<int:survey_id>/', views.survey_view, name='survey_view'),
    path('<int:survey_id>/delete', views.survey_delete, name='survey_delete'),
    path('take/<int:survey_id>', views.survey_take_menu, name='survey_take'),
    path('take/<int:survey_id>/nominations',
         views.survey_take_nominations, name='survey_take_nominations'),
    path('take/<int:survey_id>/perceptions',
         views.survey_take_perceptions, name='survey_take_perceptions'),
    path('take/<int:survey_id>/peerfeedback',
         views.survey_take_pf, name='survey_take_pf'),
    path('take/<int:survey_id>/questions',
         views.survey_take_qa, name='survey_take_qa'),
    path('take/<int:survey_id>/topbot5',
         views.survey_take_topbot5, name='survey_take_topbot5'),
    path('review', views.survey_review_menu, name='survey_review_menu'),
    path('review/nominations', views.survey_review_nominations,
         name='survey_review_nominations'),
    path('review/nom/search', views.nom_search_view, name='nom_search_view'),
    path('review/qa/search', views.qa_search_view, name='qa_search_view'),
    path('review/topbot5/search', views.topbot5_search_view,
         name='topbot5_search_view'),
    path('review/questions', views.survey_review_questions,
         name='survey_review_questions'),
    path('review/topbot5', views.survey_review_topbot5,
         name='survey_review_topbot5'),
    path('export/survey_question_responses', views.dump_csv_survey_question_data,
         name='export_survey_question_responses'),
    path('export/survey_nomination_responses', views.dump_csv_survey_nomination_data,
         name='export_survey_nomination_responses'),
    path('export/survey_topbot5_responses', views.dump_csv_survey_topbot5_data,
         name='export_survey_topbot5_responses'),
    path('export/survey_pf_responses', views.dump_csv_survey_pf_data,
         name='export_survey_pf_responses'),
    path('export/survey_perception_responses', views.dump_csv_survey_perception_data,
         name='export_survey_perception_responses'),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined
