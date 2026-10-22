
from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path(
        "student/",
        views.assessment_list,
        name="assessment_list",
    ),
    path(
        "student/<int:assessment_id>/start/",
        views.start_assessment,
        name="start_assessment",
    ),
    path(
        "attempt/<int:attempt_id>/",
        views.take_assessment,
        name="take_assessment",
    ),
    path(
        "attempt/<int:attempt_id>/save/",
        views.save_response,
        name="save_response",
    ),
    path(
        "attempt/<int:attempt_id>/submit/",
        views.submit_assessment,
        name="submit_assessment",
    ),
    path(
        "attempt/<int:attempt_id>/result/",
        views.assessment_result,
        name="assessment_result",
    ),
]