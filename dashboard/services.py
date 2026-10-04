from django.db.models import Count
from django.utils import timezone

from internships.models import Application

from django.db.models import Count
from django.db.models.functions import TruncMonth

from internships.models import Application


def get_application_metrics(university=None):
    queryset = Application.objects.all()

    # ==========================================
    # UNIVERSITY FILTER
    # ==========================================

    if university is not None:
        queryset = queryset.filter(
            student__university=university
        )

    # ==========================================
    # BASIC COUNTS
    # ==========================================

    total = queryset.count()

    pending = queryset.filter(
        status="pending"
    ).count()

    accepted = queryset.filter(
        status="accepted"
    ).count()

    rejected = queryset.filter(
        status="rejected"
    ).count()

    # ==========================================
    # RATES
    # ==========================================

    acceptance_rate = (
        accepted / total * 100
        if total
        else 0
    )

    rejection_rate = (
        rejected / total * 100
        if total
        else 0
    )

    pending_rate = (
        pending / total * 100
        if total
        else 0
    )

    # ==========================================
    # UNIQUE STUDENTS WHO APPLIED
    # ==========================================

    students_applied = (
        queryset
        .values("student")
        .distinct()
        .count()
    )

    # ==========================================
    # APPLICATIONS TODAY
    # ==========================================

    today = queryset.filter(
        applied_date__date=timezone.localdate()
    ).count()

    # ==========================================
    # APPLICATIONS THIS MONTH
    # ==========================================

    now = timezone.now()

    this_month = queryset.filter(
        applied_date__year=now.year,
        applied_date__month=now.month,
    ).count()

    # ==========================================
    # APPLICATIONS BY COURSE
    # ==========================================

    applications_by_course = list(
        queryset
        .values("student__course")
        .annotate(
            total=Count("id")
        )
        .order_by("-total")
    )

    # ==========================================
    # APPLICATIONS BY YEAR OF STUDY
    # ==========================================

    applications_by_year = list(
        queryset
        .values("student__year_of_study")
        .annotate(
            total=Count("id")
        )
        .order_by(
            "student__year_of_study"
        )
    )

    # ==========================================
    # APPLICATIONS BY MONTH
    # ==========================================

    monthly_queryset = (
        queryset
        .annotate(
            month=TruncMonth(
                "applied_date"
            )
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    applications_by_month = []

    for item in monthly_queryset:

        applications_by_month.append(
            {
                "month": item["month"].strftime(
                    "%b %Y"
                ),
                "total": item["total"],
            }
        )

    # ==========================================
    # RETURN JSON-SAFE DATA
    # ==========================================

    return {
        "total": total,

        "pending": pending,

        "accepted": accepted,

        "rejected": rejected,

        "students_applied": students_applied,

        "today": today,

        "this_month": this_month,

        "acceptance_rate": round(
            acceptance_rate,
            1,
        ),

        "rejection_rate": round(
            rejection_rate,
            1,
        ),

        "pending_rate": round(
            pending_rate,
            1,
        ),

        "applications_by_course": (
            applications_by_course
        ),

        "applications_by_year": (
            applications_by_year
        ),

        "applications_by_month": (
            applications_by_month
        ),
    }
