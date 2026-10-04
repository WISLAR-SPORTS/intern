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

from .forms import InternshipApplicationForm
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

    notification_list = (
        Notification.objects
        .filter(
            student=student,
            is_deleted=False
        )
        .select_related(
            "application",
            "internship",
            "internship__company"
        )
        .order_by("-created_at")
    )

    # Mark all notifications as read when the page is opened
    Notification.objects.filter(
        student=student,
        is_deleted=False,
        is_read=False
    ).update(
        is_read=True
    )

    return render(
        request,
        "students/notifications.html",
        {
            "notifications": notification_list,
            "unread_count": 0,
        }
    )


@login_required
def mark_notification_read(request, notification_id):

    student = request.user.student

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        student=student,
        is_deleted=False
    )

    notification.is_read = True

    notification.save(
        update_fields=["is_read"]
    )

    # Go to the application if the notification belongs to one
    if notification.application:
        return redirect(
            "internship:application_detail",
            notification.application.id
        )

    # Otherwise go to the internship
    if notification.internship:
        return redirect(
            "internship:internship_detail",
            notification.internship.id
        )

    return redirect(
        "internship:notifications"
    )


@login_required
def delete_notification(request, notification_id):

    student = request.user.student

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        student=student
    )

    notification.is_deleted = True

    notification.save(
        update_fields=["is_deleted"]
    )

    return redirect(
        "internship:notifications"
    )

