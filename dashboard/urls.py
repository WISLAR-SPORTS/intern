from django.urls import path

from . import views


app_name = "dashboard"


urlpatterns = [
    path(
        "studentdashboard/",
        views.student_dashboard,
        name="student-dashboard",
    ),
    path("", views.intro, name="intro"),
    path("home/", views.home, name="home"),
     path(
        "applications/",
        views.my_applications,
        name="my_applications"
    ),
]
