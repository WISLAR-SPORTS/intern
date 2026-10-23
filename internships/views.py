from rest_framework.generics import ListAPIView
from .models import Internship
from .serializers import InternshipSerializer


class InternshipListView(ListAPIView):

    serializer_class = InternshipSerializer


    def get_queryset(self):

        queryset = Internship.objects.filter(
            active=True
        )


        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )


        location = self.request.GET.get("location")

        if location:
            queryset = queryset.filter(
                location__icontains=location
            )


        return queryset

from .models import Internship, Application
from students.models import Student

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from students.models import Student

from .forms import InternshipApplicationForm
from .models import Internship, Application, ApplicationAnswer


from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.utils import timezone

from students.models import Student

from .forms import InternshipApplicationForm, ApplicationReviewForm
from .models import (
    Internship,
    Application,
    ApplicationAnswer,
    
)


@login_required
def apply_for_internship(request, internship_id):

    internship = get_object_or_404(
        Internship,
        id=internship_id,
        active=True
    )

    # -----------------------------------------
    # Get student profile
    # -----------------------------------------

    try:
        student = request.user.student

    except Student.DoesNotExist:

        messages.error(
            request,
            "You need a student profile before applying."
        )

        return redirect(
            "dashboard:student-dashboard"
        )

    # -----------------------------------------
    # Check deadline
    # -----------------------------------------

    if internship.deadline < timezone.localdate():

        messages.error(
            request,
            "This internship application deadline has passed."
        )

        return redirect(
            "dashboard:student-dashboard"
        )

    # -----------------------------------------
    # Check if already applied
    # -----------------------------------------

    if Application.objects.filter(
        student=student,
        internship=internship
    ).exists():

        messages.warning(
            request,
            "You have already applied for this internship."
        )

        return redirect(
            "dashboard:student-dashboard"
        )

    # -----------------------------------------
    # POST
    # -----------------------------------------

    if request.method == "POST":

        form = InternshipApplicationForm(
            request.POST,
            request.FILES,
            internship=internship
        )

        if form.is_valid():

            application = Application.objects.create(
                student=student,
                internship=internship,
                cover_letter=form.cleaned_data["cover_letter"],
            )

            # -----------------------------------------
            # Save custom field answers
            # -----------------------------------------

            for field in internship.custom_fields.all().order_by(
                "order",
                "id"
            ):

                field_name = f"field_{field.id}"

                answer = form.cleaned_data.get(field_name)

                uploaded_file = None

                if field.field_type == "file":
                    uploaded_file = request.FILES.get(field_name)

                if answer or uploaded_file:

                    ApplicationAnswer.objects.create(
                        application=application,
                        field=field,
                        answer="" if uploaded_file else str(answer),
                        file=uploaded_file
                    )

            messages.success(
                request,
                "Your application was submitted successfully!"
            )

            return redirect(
                "dashboard:student-dashboard"
            )

        else:

            messages.error(
                request,
                "Please correct the errors below and try again."
            )

    # -----------------------------------------
    # GET
    # -----------------------------------------

    else:

        form = InternshipApplicationForm(
            internship=internship
        )

    # -----------------------------------------
    # Render application page
    # -----------------------------------------

    return render(
        request,
        "internships/apply.html",
        {
            "internship": internship,
            "form": form,
        }
    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from students.models import Notification
@login_required
def notifications(request):

    student = request.user.student

    notification_list = list(
        Notification.objects
        .filter(
            student=student,
            is_deleted=False,
        )
        .select_related(
            "application",
            "internship",
            "internship__company",
        )
        .order_by("-created_at")
    )

    unread_count = sum(
        1
        for notification in notification_list
        if not notification.is_read
    )

    # Mark notifications as read when the page is opened
    Notification.objects.filter(
        student=student,
        is_deleted=False,
        is_read=False,
    ).update(
        is_read=True
    )

    return render(
        request,
        "students/notifications.html",
        {
            "notifications": notification_list,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_notification_read(request, notification_id):

    student = request.user.student

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        student=student,
        is_deleted=False,
    )

    notification.is_read = True

    notification.save(
        update_fields=["is_read"]
    )

    # Application notification
    if notification.application:

        return redirect(
            "internships:application_detail",
            notification.application.id,
        )

    # Internship notification
    if notification.internship:

        return redirect(
            "internships:internship_detail",
            notification.internship.id,
        )

    return redirect(
        "internships:notifications"
    )


@login_required
def delete_notification(request, notification_id):

    student = request.user.student

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        student=student,
        is_deleted=False,
    )

    notification.is_deleted = True

    notification.save(
        update_fields=["is_deleted"]
    )

    return redirect(
        "internships:notifications"
    )

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator

from django.utils.dateparse import parse_date
from .ai_evaluation import evaluate_application
import logging

logger = logging.getLogger(__name__)

from .models import Application    
@staff_member_required


def ai_evaluation(request):

    # Automatically evaluate applications that have not been scored.
    pending_applications = (
        Application.objects
        .filter(ai_evaluated_at__isnull=True)
        .select_related("student", "internship")
        .order_by("applied_date", "pk")
    )

    for application in pending_applications.iterator():
        result = evaluate_application(application)

        if result.get("success"):
            logger.info(
                "AI evaluation succeeded for application ID %s: %s/100",
                application.pk,
                result["ai_score"],
            )
        else:
            logger.error(
                "AI evaluation failed for application ID %s",
                application.pk,
            )

    # Base queryset
    queryset = Application.objects.select_related(
        "student",
        "internship",
    ).order_by("-applied_date")

    # Summary counts (all applications, independent of filters)
    total_applications = queryset.count()
    evaluated_count = queryset.filter(
        ai_evaluated_at__isnull=False
    ).count()
    not_evaluated_count = total_applications - evaluated_count
    pending_review_count = queryset.filter(
        reviewed_at__isnull=True
    ).count()

    # Search
    search = request.GET.get("q", "").strip()

    if search:
        if search.isdigit():
            queryset = queryset.filter(
                Q(pk=int(search))
                | Q(student_id=int(search))
                | Q(internship_id=int(search))
            )
        else:
            queryset = queryset.none()

    # Application status
    status = request.GET.get("status", "")
    valid_statuses = dict(Application.STATUS)

    if status in valid_statuses:
        queryset = queryset.filter(status=status)

    # Internship filter
    internship_id = request.GET.get("internship", "").strip()
    internships = Internship.objects.all().order_by("id")

    if internship_id.isdigit():
        queryset = queryset.filter(
            internship_id=int(internship_id)
        )
    else:
        internship_id = ""

    # Application date range
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()

    parsed_start_date = parse_date(start_date) if start_date else None
    parsed_end_date = parse_date(end_date) if end_date else None

    if parsed_start_date:
        queryset = queryset.filter(
            applied_date__date__gte=parsed_start_date
        )

    if parsed_end_date:
        queryset = queryset.filter(
            applied_date__date__lte=parsed_end_date
        )

    # AI evaluation filter
    evaluation = request.GET.get("evaluation", "")

    if evaluation == "evaluated":
        queryset = queryset.filter(
            ai_evaluated_at__isnull=False
        )
    elif evaluation == "not_evaluated":
        queryset = queryset.filter(
            ai_evaluated_at__isnull=True
        )

    # AI score filters
    min_score = request.GET.get("min_score", "").strip()
    max_score = request.GET.get("max_score", "").strip()

    if min_score:
        try:
            value = int(min_score)
            if 0 <= value <= 100:
                queryset = queryset.filter(ai_score__gte=value)
        except ValueError:
            pass

    if max_score:
        try:
            value = int(max_score)
            if 0 <= value <= 100:
                queryset = queryset.filter(ai_score__lte=value)
        except ValueError:
            pass

    # Preserve active filters during pagination
    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    paginator = Paginator(queryset, 20)
    applications = paginator.get_page(request.GET.get("page"))

    context = {
        "applications": applications,
        "internships": internships,
        "total_applications": total_applications,
        "evaluated_count": evaluated_count,
        "not_evaluated_count": not_evaluated_count,
        "pending_review_count": pending_review_count,
        "status_choices": Application.STATUS,
        "filters": {
            "q": search,
            "status": status,
            "internship": internship_id,
            "start_date": start_date,
            "end_date": end_date,
            "evaluation": evaluation,
            "min_score": min_score,
            "max_score": max_score,
        },
        "query_string": query_string,
    }

    return render(
        request,
        "admin/applications/ai_evaluation.html",
        context,
    )