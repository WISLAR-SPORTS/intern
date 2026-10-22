from django.contrib import admin
from django.utils import timezone
from .models import Internship, InternshipField, Application, ApplicationAnswer
from django.urls import path, reverse
from django.utils.html import format_html
from students.models import Notification
from .brevo_email import send_shortlist_email

class InternshipFieldInline(admin.TabularInline):
    model = InternshipField
    extra = 1
    fields = (
        "label",
        "field_type",
        "required",
        "options",
        "order",
    )


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "internship_type",
        "location",
        "deadline",
        "active",
        "created_at",
    )

    list_filter = (
        "internship_type",
        "active",
        "deadline",
    )

    search_fields = (
        "title",
        "company__name",
        "location",
        "required_skills",
    )

    inlines = [
        InternshipFieldInline,
    ]

from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils import timezone

from .forms import ApplicationReviewForm



from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Application
from .forms import ApplicationReviewForm



# ==========================================================
# NOTIFICATION HELPER
# ==========================================================

def create_application_notification(
    application,
    action,
    title,
    message,
):
    Notification.objects.create(
        student=application.student,
        notification_type="application",
        action=action,
        title=title,
        message=message,
        application=application,
        internship=application.internship,
    )


# ==========================================================
# APPLICATION ADMIN
# ==========================================================

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "internship",
        "status",
        "score",
        "applied_date",
        "reviewed_at",
        "review_button",
    )

    list_filter = (
        "status",
        "internship",
        "applied_date",
    )

    search_fields = (
        "student__user__username",
        "student__user__first_name",
        "student__user__last_name",
        "student__user__email",
        "student__registration_number",
        "internship__title",
    )

    actions = [
        "approve_and_place",
    ]

    # ======================================================
    # BULK APPROVE / PLACE
    # ======================================================

    @admin.action(
        description="Approve / Place selected students"
    )
    def approve_and_place(self, request, queryset):

        # Only shortlisted applications can be placed
        applications = queryset.filter(
            status="shortlisted"
        )

        if not applications.exists():

            self.message_user(
                request,
                "No shortlisted applications were selected.",
                messages.ERROR,
            )

            return

        # Store selected application IDs temporarily
        request.session["placement_application_ids"] = list(
            applications.values_list(
                "id",
                flat=True
            )
        )

        # Go to confirmation page
        return redirect(
            "admin:application-approve-place"
        )

    # ======================================================
    # CUSTOM ADMIN URLS
    # ======================================================

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            # ----------------------------------------------
            # REVIEW APPLICATION
            # ----------------------------------------------

            path(
                "<int:application_id>/review/",
                self.admin_site.admin_view(
                    self.review_application
                ),
                name="application-review",
            ),

            # ----------------------------------------------
            # APPROVE / PLACE CONFIRMATION
            # ----------------------------------------------

            path(
                "approve-place/",
                self.admin_site.admin_view(
                    self.approve_place
                ),
                name="application-approve-place",
            ),
        ]

        return custom_urls + urls

    # ======================================================
    # REVIEW BUTTON
    # ======================================================

    @admin.display(description="Action")
    def review_button(self, obj):

        url = reverse(
            "admin:application-review",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" href="{}">Review</a>',
            url,
        )

    # ======================================================
    # APPROVE / PLACE CONFIRMATION
    # ======================================================

    def approve_place(self, request):

        application_ids = request.session.get(
            "placement_application_ids",
            []
        )

        # ----------------------------------------------
        # Nothing selected
        # ----------------------------------------------

        if not application_ids:

            messages.error(
                request,
                "No applications were selected for placement.",
            )

            return redirect(
                "admin:internships_application_changelist"
            )

        # ----------------------------------------------
        # Get shortlisted applications
        # ----------------------------------------------

        applications = (
            Application.objects
            .filter(
                id__in=application_ids,
                status="shortlisted",
            )
            .select_related(
                "student",
                "student__user",
                "internship",
            )
        )

        # ----------------------------------------------
        # CONFIRM / CANCEL
        # ----------------------------------------------

        if request.method == "POST":

            action = request.POST.get("action")

            # ==========================================
            # CONFIRM PLACEMENT
            # ==========================================

            if action == "confirm":

                placed_count = 0

                for application in applications:

                    application.status = "accepted"
                    application.reviewed_by = request.user
                    application.reviewed_at = timezone.now()

                    application.save(
                        update_fields=[
                            "status",
                            "reviewed_by",
                            "reviewed_at",
                        ]
                    )

                    # ----------------------------------
                    # SEND STUDENT NOTIFICATION
                    # ----------------------------------

                    create_application_notification(
                        application=application,
                        action="application_accepted",
                        title="Internship Placement Approved",
                        message=(
                            f"Congratulations! You have been "
                            f"approved and placed for the "
                            f"internship position "
                            f"'{application.internship.title}'."
                        ),
                    )

                    placed_count += 1

                # --------------------------------------
                # Clear session
                # --------------------------------------

                request.session.pop(
                    "placement_application_ids",
                    None,
                )

                messages.success(
                    request,
                    f"{placed_count} student(s) have been "
                    f"approved and placed successfully. "
                    f"Placement notifications have been sent.",
                )

                return redirect(
                    "admin:internships_application_changelist"
                )

            # ==========================================
            # CANCEL
            # ==========================================

            elif action == "cancel":

                request.session.pop(
                    "placement_application_ids",
                    None,
                )

                messages.info(
                    request,
                    "Placement action cancelled.",
                )

                return redirect(
                    "admin:internships_application_changelist"
                )

        # ==================================================
        # CONFIRMATION PAGE
        # ==================================================

        context = {
            **self.admin_site.each_context(request),

            "title": "Confirm Internship Placement",

            "applications": applications,

            "placement_count": applications.count(),
        }

        return render(
            request,
            "admin/applications/confirm_placement.html",
            context,
        )

    # ======================================================
    # REVIEW APPLICATION
    # ======================================================

    def review_application(
        self,
        request,
        application_id,
    ):

        application = get_object_or_404(
            Application.objects.select_related(
                "student",
                "student__user",
                "internship",
                "reviewed_by",
            ).prefetch_related(
                "answers__field"
            ),
            pk=application_id,
        )

        # ==================================================
        # HANDLE POST REQUEST
        # ==================================================

        if request.method == "POST":

            action = request.POST.get("action")

            # ==================================================
            # SAVE REVIEW
            # ==================================================

            if action == "save_review":

                old_status = application.status

                form = ApplicationReviewForm(
                    request.POST,
                    instance=application,
                )

                if form.is_valid():

                    application = form.save(
                        commit=False
                    )

                    # ------------------------------------------
                    # PENDING → UNDER REVIEW
                    # ------------------------------------------

                    if application.status == "pending":

                        application.status = "under_review"

                    # ------------------------------------------
                    # RECORD REVIEWER
                    # ------------------------------------------

                    application.reviewed_by = request.user
                    application.reviewed_at = timezone.now()

                    application.save(
                        update_fields=[
                            "score",
                            "reviewer_notes",
                            "status",
                            "reviewed_by",
                            "reviewed_at",
                        ]
                    )

                    # ------------------------------------------
                    # NOTIFY STUDENT
                    # ------------------------------------------

                    if (
                        old_status == "pending"
                        and application.status == "under_review"
                    ):

                        create_application_notification(
                            application=application,
                            action="application_under_review",
                            title="Application Under Review",
                            message=(
                                f"Your application for "
                                f"{application.internship.title} "
                                f"is now under review."
                            ),
                        )

                    messages.success(
                        request,
                        "Review saved successfully.",
                    )

                    return redirect(request.path)

            # ==================================================
            # SHORTLIST
            # ==================================================

            
            # ==================================================
            # SHORTLIST
            # ==================================================

            elif action == "shortlist":

                if application.status == "under_review":

                    application.status = "shortlisted"
                    application.reviewed_by = request.user
                    application.reviewed_at = timezone.now()

                    application.save(
                        update_fields=[
                            "status",
                            "reviewed_by",
                            "reviewed_at",
                        ]
                    )

                    # ------------------------------------------
                    # SEND BREVO EMAIL
                    # ------------------------------------------

                    email_sent = send_shortlist_email(
                        application
                    )

                    if email_sent:
                        messages.success(
                            request,
                            "Shortlist email sent successfully "
                            "to the student.",
                        )
                    else:
                        messages.warning(
                            request,
                            "The application was shortlisted, "
                            "but the email could not be sent. "
                            "Check your Brevo configuration "
                            "and application logs.",
                        )

                    # ------------------------------------------
                    # IN-APP NOTIFICATION
                    # ------------------------------------------

                    create_application_notification(
                        application=application,
                        action="application_shortlisted",
                        title="Shortlisted for Interview",
                        message=(
                            f"Congratulations! Your application "
                            f"for {application.internship.title} "
                            f"has been shortlisted for an interview."
                        ),
                    )

                    messages.success(
                        request,
                        "Application shortlisted for interview.",
                    )

                else:

                    messages.error(
                        request,
                        "Only applications under review "
                        "can be shortlisted.",
                    )

                return redirect(request.path)

            # ==================================================
            # REJECT
            # ==================================================

            elif action == "reject":

                if application.status in (
                    "pending",
                    "under_review",
                ):

                    application.status = "rejected"
                    application.reviewed_by = request.user
                    application.reviewed_at = timezone.now()

                    application.save(
                        update_fields=[
                            "status",
                            "reviewed_by",
                            "reviewed_at",
                        ]
                    )

                    create_application_notification(
                        application=application,
                        action="application_rejected",
                        title="Application Update",
                        message=(
                            f"Thank you for applying for "
                            f"{application.internship.title}. "
                            f"Unfortunately, your application "
                            f"was not successful at this stage."
                        ),
                    )

                    messages.success(
                        request,
                        "Application rejected.",
                    )

                else:

                    messages.error(
                        request,
                        "This application cannot be rejected "
                        "at this stage.",
                    )

                return redirect(request.path)

        # ==================================================
        # GET REQUEST
        # ==================================================

        form = ApplicationReviewForm(
            instance=application,
        )

        context = {
            "application": application,
            "answers": application.answers.all(),
            "form": form,
            **self.admin_site.each_context(request),
        }

        return render(
            request,
            "admin/applications/application_review.html",
            context,
        )
@admin.register(ApplicationAnswer)
class ApplicationAnswerAdmin(admin.ModelAdmin):

    list_display = (
        "application",
        "field",
        "answer",
        "file",
    )

    search_fields = (
        "application__student__user__username",
        "application__student__registration_number",
        "field__label",
    )