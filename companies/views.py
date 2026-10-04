from django.shortcuts import render
from students.models import University
from students.models import Student
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from students.models import Student
from internships.models import Company
from django.utils import timezone
from django.shortcuts import render
from .models import LandingPageSettings, Company
def landing_page(request):
    settings = LandingPageSettings.objects.first()

    universities = list(
        University.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).values(
            "id",
            "name",
            "latitude",
            "longitude",
        )
    )

    companies = list(
        Company.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).values(
            "id",
            "company_name",
            "latitude",
            "longitude",
        )
    )

    context = {
        "settings": settings,
        "universities": universities,
        "companies": companies,
        "university_count": University.objects.count(),
        "company_count": Company.objects.count(),
        "student_count": 0,
        "internship_count": 0,
    }

    return render(request, "home.html", context)

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from .models import Company

from internships.models import Internship
from students.models import Application

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from .models import Company
from internships.models import Internship
from students.models import Application


def company_user_required(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.is_staff
        and (
            user.is_superuser
            or user.role == "company"
        )
    )


@staff_member_required
@user_passes_test(company_user_required)
def company_dashboard(request):

    user = request.user

    # ==========================================
    # COMPANY
    # ==========================================

    if user.is_superuser:
        company = None
    else:
        company = user.company

    # ==========================================
    # INTERNSHIPS & APPLICATIONS
    # ==========================================

    if company:

        internships = Internship.objects.filter(
            company=company
        )

        applications = Application.objects.filter(
            internship__company=company
        )

    else:

        internships = Internship.objects.all()

        applications = Application.objects.all()

    # ==========================================
    # INTERNSHIP STATISTICS
    # ==========================================

    total_internships = internships.count()

    active_internships = internships.filter(
        active=True
    ).count()

    closed_internships = internships.filter(
        active=False
    ).count()

    # ==========================================
    # APPLICATION STATISTICS
    # ==========================================

    total_applications = applications.count()

    pending_applications = applications.filter(
        status="pending"
    ).count()

    shortlisted_applications = applications.filter(
        status="shortlisted"
    ).count()

    accepted_applications = applications.filter(
        status="accepted"
    ).count()

    rejected_applications = applications.filter(
        status="rejected"
    ).count()

    # ==========================================
    # RECENT APPLICATIONS
    # ==========================================

    recent_applications = (
        applications
        .select_related(
            "student",
            "internship",
        )
        .order_by("-applied_date")[:10]
    )

    # ==========================================
    # CONTEXT
    # ==========================================

    context = {

        "title": "Company Dashboard",

        "company": company,

        "total_internships":
            total_internships,

        "active_internships":
            active_internships,

        "closed_internships":
            closed_internships,

        "total_applications":
            total_applications,

        "pending_applications":
            pending_applications,

        "shortlisted_applications":
            shortlisted_applications,

        "accepted_applications":
            accepted_applications,

        "rejected_applications":
            rejected_applications,

        "recent_applications":
            recent_applications,
    }

    return render(
        request,
        "dashboard/company_dashboard.html",
        context,
    )

