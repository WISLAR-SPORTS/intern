from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.service import is_student
from internships.models import Internship
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render, redirect

from internships.models import Internship, Application
from students.models import Student

from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef



@login_required
def student_dashboard(request):

    if not is_student(request.user):
        return redirect("login")

    student = request.user.student

    application_exists = Application.objects.filter(
        student=student,
        internship=OuterRef("pk")
    )

    internships = (
        Internship.objects
        .filter(active=True)
        .select_related("company")
        .annotate(
            already_applied=Exists(application_exists)
        )
        .order_by("-created_at")
    )

    context = {
        "internships": internships,
    }

    return render(
        request,
        "dashboard/student-dashboard.html",
        context
    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_application_metrics
from django.shortcuts import redirect, render
from accounts.service import get_login_redirect


@login_required
def university_dashboard(request):

    if request.user.is_superuser:

        university = None

    elif request.user.role == "university":

        university = request.user.university

    else:

        return redirect(
            get_login_redirect(request.user)
        )

    application_metrics = get_application_metrics(
        university=university
    )

    return render(
        request,
        "dashboard/university.html",
        {
            "application_metrics": application_metrics,
        },
    )
def intro(request):
    return render(request, "dashboard/intro.html")


def home(request):
    return render(request, "dashboard/home.html")

# views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from internships.models import Application


@login_required
def my_applications(request):
    student = request.user.student

    applications = (
        Application.objects
        .filter(student=student)
        .select_related(
            "internship",
            "internship__company",
        )
        .prefetch_related(
            "answers__field",
        )
        .order_by("-applied_date")
    )

    context = {
        "applications": applications,
        "total_applications": applications.count(),
        "pending_count": applications.filter(status="pending").count(),
        "accepted_count": applications.filter(status="accepted").count(),
        "rejected_count": applications.filter(status="rejected").count(),
    }

    return render(
        request,
        "students/application.html",
        context
    )
