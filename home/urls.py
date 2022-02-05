from django.urls import path, reverse_lazy
from . import views

app_name = "home"
urlpatterns = [
    path("", views.home_view, name="home_page"),
    path("unauthorized", views.unauthorized_view, name="unauthorized_view"),
    path("reset_password", views.reset_password, name="reset_password"),
]
