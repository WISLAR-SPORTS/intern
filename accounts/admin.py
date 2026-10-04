from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from internships.models import Application, Internship, InternshipField, ApplicationAnswer
from companies.models import Company
from django.db.models import Q
from .models import User
from django.contrib import admin
from .models import OTPCode, LoginAttempt

from django.contrib import admin
from .models import User, UserConsent, LegalDocument


from django.contrib import admin

from .models import User, UserConsent, LegalDocument


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "document_type",
        "version",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "document_type",
        "is_active",
    )

    search_fields = (
        "title",
        "content",
        "version",
    )

    ordering = (
        "-updated_at",
    )


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "terms_version",
        "privacy_version",
        "accepted_at",
    )

    list_filter = (
        "terms_version",
        "privacy_version",
        "accepted_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "accepted_at",
        "ip_address",
        "user_agent",
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code",
        "purpose",
        "created_at",
        "expires_at",
        "attempts",
        "used",
    )
    list_filter = ("purpose", "used", "created_at")
    search_fields = ("user__username", "user__email", "code")
    readonly_fields = ("created_at",)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "successful",
        "created_at",
    )
    list_filter = ("successful", "created_at")
    search_fields = ("user__username", "user__email", "ip_address")
    readonly_fields = ("created_at",)



@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Role",
            {
                "fields": (
                    "role",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Role",
            {
                "fields": (
                    "role",
                ),
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        print(
            "ADMIN USER:",
            request.user.username,
            request.user.role,
            request.user.is_superuser,
        )

        if request.user.is_superuser:
            return qs

        if request.user.role == "company":
            return qs.filter(
                pk=request.user.pk
            )

        return qs.none()
def get_company(user):
    """
    Return the company attached to this user.
    Returns None if the user has no company.
    """
    try:
        return user.company
    except AttributeError:
        return None   
    
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):

    list_display = (
        "log_date",
        "performed_by",
        "model_name",
        "object_name",
        "action",
    )

    list_filter = (
        "action_flag",
        "content_type",
    )

    search_fields = (
        "object_repr",
        "change_message",
        "user__username",
    )

    readonly_fields = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    # -------------------------------
    # TABLE HEADINGS
    # -------------------------------

    @admin.display(description="Date & Time", ordering="action_time")
    def log_date(self, obj):
        return obj.action_time

    @admin.display(description="Performed By", ordering="user")
    def performed_by(self, obj):
        return obj.user

    @admin.display(description="Model", ordering="content_type")
    def model_name(self, obj):
        return obj.content_type

    @admin.display(description="Object", ordering="object_repr")
    def object_name(self, obj):
        return obj.object_repr

    @admin.display(description="Action", ordering="action_flag")
    def action(self, obj):
        return obj.get_action_flag_display()

    # -------------------------------
    # LOGENTRY IS READ ONLY
    # -------------------------------

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # -------------------------------
    # YOUR QUERYSET
    # -------------------------------

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company = get_company(request.user)

        if company is None:
            return qs.none()

        internship_ids = Internship.objects.filter(
            company=company
        ).values_list("pk", flat=True)

        field_ids = InternshipField.objects.filter(
            internship__company=company
        ).values_list("pk", flat=True)

        application_ids = Application.objects.filter(
            internship__company=company
        ).values_list("pk", flat=True)

        answer_ids = ApplicationAnswer.objects.filter(
            application__internship__company=company
        ).values_list("pk", flat=True)

        return qs.filter(
            Q(
                content_type__app_label="internships",
                content_type__model="internship",
                object_id__in=internship_ids,
            )
            |
            Q(
                content_type__app_label="internships",
                content_type__model="internshipfield",
                object_id__in=field_ids,
            )
            |
            Q(
                content_type__app_label="internships",
                content_type__model="application",
                object_id__in=application_ids,
            )
            |
            Q(
                content_type__app_label="internships",
                content_type__model="applicationanswer",
                object_id__in=answer_ids,
            )
        )