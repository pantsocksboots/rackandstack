from django.urls import path, reverse_lazy
from . import views

app_name='rubric'
urlpatterns = [
    path('evolutions/', views.evolution_list, name='evolution_list'),
    path('evolutions/create/', views.evolution_create, name='evolution_create'),
    path('evolutions/create_obj/', views.obj_evolution_create, name='obj_evolution_create'),
    path('evolutions/<int:evolution_id>/', views.evolution_detail, name='evolution_detail'),
    path('evolutions/<int:evolution_id>/edit', views.evolution_edit, name='evolution_edit'),
    path('evolutions/<int:evolution_id>/delete', views.evolution_delete, name='evolution_delete'),
    path('evolutions/csv_dump', views.evolution_csv_dump, name='evolution_csv_dump'),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined