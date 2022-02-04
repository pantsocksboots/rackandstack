from django.urls import path, reverse_lazy
from . import views

app_name = "home"
urlpatterns = [
    path("", views.home_view, name="home_page"),
    path("unauthorized", views.unauthorized_view, name="unauthorized_view"),
]
