from django.urls import path, reverse_lazy
from . import views

app_name = "stucon"
urlpatterns = [
    path("", views.bulk_edit_list, name="student_list"),
    path("create", views.create_student_user, name="create_student_user"),
    path("<int:student_id>/edit", views.student_edit, name="student_edit"),
    path("<int:student_id>/", views.student_view, name="student_view"),
    path("<int:student_id>/delete", views.student_delete, name="student_delete"),
    path("bulk_create", views.bulk_create_students, name="bulk_create_students"),
    path("bulk_edit", views.bulk_edit_list, name="bulk_edit_list"),
    path("bulk_edit_results", views.bulk_edit_results, name="bulk_edit_results"),
    path(
        "bulk_status_update/<int:new_status>",
        views.bulk_status_update,
        name="bulk_status_update",
    ),
    path(
        "<int:student_id>/status_comment_view_checked",
        views.status_comment_view_checked,
        name="status_comment_view_checked",
    ),
    path(
        "<int:student_id>/status_comment_view_unchecked",
        views.status_comment_view_unchecked,
        name="status_comment_view_unchecked",
    ),
    path("csv_export", views.dump_csv_student_data, name="dump_student_data"),
    path("upload_image", views.upload_image, name="upload_image"),
    path(
        "<int:cohort>/student_directory",
        views.student_directory,
        name="student_directory",
    ),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined
