from django.urls import path

from . import views


app_name = "students"


urlpatterns = [

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),

    path(
        "profile/",
        views.student_profile,
        name="student_profile",
    ),
  path(
        "university/",
        views.university_dashboard,
        name="university_dashboard",
    ),
]
