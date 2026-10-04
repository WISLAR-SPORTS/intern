from django.urls import path
from . import views
from dashboard.views import student_dashboard

app_name = "internships"

urlpatterns = [

   
   
        path(
        "apply/<int:internship_id>/",
        views.apply_for_internship,
        name="apply_for_internship",
    ),
  path(
        "notifications/",
        views.notifications,
        name="notifications"
    ),
     path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),

    path(
        "notifications/<int:notification_id>/delete/",
        views.delete_notification,
        name="delete_notification"
    ),

]