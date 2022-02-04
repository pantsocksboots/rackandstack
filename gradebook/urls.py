from django.urls import path, reverse_lazy
from . import views

app_name='gradebook'
urlpatterns = [
    path('', views.gradebook_menu, name='gradebook_menu'),
    path('select_evo/', views.gradebook_selection, name='gradebook_selection'),
    path('grade_evo_list/<int:cohort_id>/<int:evolution_id>', views.grade_evo_list, name='grade_evo_list'),
    path('grade_evo/<int:student_id>/<int:evolution_id>', views.grade_evo, name='grade_evo'),
    path('grade_evo/<int:student_id>/<int:evolution_id>/delete', views.grade_evo_delete, name='grade_evo_delete'),
    path('csv_dump', views.gradebook_csv_dump, name='gradebook_csv_dump'),
]