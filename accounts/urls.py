from django.urls import path

from . import views
from dashboard.views import student_dashboard
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "login/",
        views.web_login,
        name="login",
    ),

      path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),

    path(
        "studentdashboard/",
        student_dashboard,
        name="student-dashboard",
    ),


    # Step 1
    path(
        "login/",
        views.web_login,
        name="login",
    ),

    # Step 2
    path(
        "login/method/",
        views.login_method,
        name="login_method",
    ),

    # Password
    path(
        "login/password/",
        views.password_login,
        name="password_login",
    ),

    # OTP
    path(
        "login/otp/",
        views.request_otp,
        name="request_otp",
    ),

    path(
        "login/otp/verify/",
        views.verify_otp,
        name="verify_otp",
    ),
      path(
        "consent/",
        views.consent_view,
        name="consent",
    ),

    path(
        "consent/accept/",
        views.accept_consent,
        name="accept_consent",
    ),

    path(
        "terms/",
        views.terms,
        name="terms",
    ),

    path(
        "privacy/",
        views.privacy,
        name="privacy",
    ),

]
