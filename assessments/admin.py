
import nested_admin

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import (
    Assessment,
    Question,
    AnswerOption,
    AssessmentAssignment,
    AssessmentAttempt,
    StudentResponse,
)
from companies.models import Company


# ==========================================================
# COMPANY LOOKUP
# ==========================================================

def get_company_for_user(user):
    if not user.is_authenticated:
        return None

    try:
        return user.company
    except Company.DoesNotExist:
        return None


def is_company_manager(user):
    return user.is_superuser or get_company_for_user(user) is not None


def assessment_queryset_for_user(user):
    qs = Assessment.objects.all()

    if user.is_superuser:
        return qs

    company = get_company_for_user(user)

    if company is None:
        return qs.none()

    return qs.filter(internship__company=company)


def assessment_is_owned_by_user(user, assessment):
    if user.is_superuser:
        return True

    company = get_company_for_user(user)

    return (
        company is not None
        and assessment.internship.company_id == company.pk
    )


# ==========================================================
# NESTED ANSWER OPTIONS
# ==========================================================

class AnswerOptionInline(nested_admin.NestedTabularInline):
    model = AnswerOption
    extra = 4
    fields = ("option_text", "is_correct")


# ==========================================================
# NESTED QUESTIONS
# ==========================================================

class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 1
    show_change_link = True
    fields = ("question_text", "marks", "order")
    inlines = [AnswerOptionInline]


# ==========================================================
# ASSESSMENTS
# ==========================================================

@admin.register(Assessment)
class AssessmentAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "title",
        "internship",
        "company_name",
        "status",
        "opens_at",
        "closes_at",
        "duration_minutes",
    )

    list_filter = ("status",)
    search_fields = ("title", "internship__title")
    readonly_fields = ("created_by", "created_at", "updated_at")
    inlines = [QuestionInline]

    fieldsets = (
        ("Assessment Details", {
            "fields": (
                "internship",
                "title",
                "description",
            )
        }),
        ("Examination Settings", {
            "fields": (
                "duration_minutes",
                "opens_at",
                "closes_at",
                "pass_mark",
                "max_attempts",
                "show_results",
            )
        }),
        ("Publication", {
            "fields": ("status",)
        }),
        ("Audit Information", {
            "fields": (
                "created_by",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Company")
    def company_name(self, obj):
        return obj.internship.company

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company = get_company_for_user(request.user)

        if company is None:
            return qs.none()

        return qs.filter(internship__company=company)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (
            db_field.name == "internship"
            and not request.user.is_superuser
        ):
            company = get_company_for_user(request.user)

            if company is None:
                kwargs["queryset"] = (
                    db_field.remote_field.model.objects.none()
                )
            else:
                kwargs["queryset"] = (
                    db_field.remote_field.model.objects.filter(
                        company=company
                    )
                )

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def has_module_permission(self, request):
        return (
            request.user.is_superuser
            or request.user.has_perm("assessments.view_assessment")
            or request.user.has_perm("assessments.add_assessment")
        )

    def has_view_permission(self, request, obj=None):
        if not (
            request.user.is_superuser
            or request.user.has_perm("assessments.view_assessment")
        ):
            return False

        if obj is not None:
            return assessment_is_owned_by_user(request.user, obj)

        return True

    def has_add_permission(self, request):
        return (
            request.user.is_superuser
            or (
                request.user.has_perm("assessments.add_assessment")
                and get_company_for_user(request.user) is not None
            )
        )

    def has_change_permission(self, request, obj=None):
        if not (
            request.user.is_superuser
            or request.user.has_perm("assessments.change_assessment")
        ):
            return False

        if obj is not None:
            return assessment_is_owned_by_user(request.user, obj)

        return True

    def has_delete_permission(self, request, obj=None):
        if not (
            request.user.is_superuser
            or request.user.has_perm("assessments.delete_assessment")
        ):
            return False

        if obj is not None:
            return assessment_is_owned_by_user(request.user, obj)

        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user

        if not request.user.is_superuser:
            company = get_company_for_user(request.user)

            if (
                company is None
                or obj.internship.company_id != company.pk
            ):
                raise PermissionDenied(
                    "You cannot manage assessments for this company."
                )

        obj.full_clean()
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Validate nested questions and options before saving.
        Correct answers remain in the database, not exposed
        to students through this admin configuration.
        """
        with transaction.atomic():
            instances = formset.save(commit=False)

            for deleted_object in formset.deleted_objects:
                deleted_object.delete()

            for instance in instances:
                instance.full_clean()
                instance.save()

            formset.save_m2m()


# ==========================================================
# STANDALONE QUESTION MANAGEMENT
# ==========================================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "assessment",
        "marks",
        "order",
    )
    list_filter = ("assessment",)
    search_fields = ("question_text", "assessment__title")
    inlines = [AnswerOptionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company = get_company_for_user(request.user)

        if company is None:
            return qs.none()

        return qs.filter(assessment__internship__company=company)

    def has_module_permission(self, request):
        return (
            request.user.is_superuser
            or request.user.has_perm("assessments.view_question")
            or request.user.has_perm("assessments.add_question")
        )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.view_question"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.assessment
            )
        )

    def has_add_permission(self, request):
        return (
            request.user.is_superuser
            or request.user.has_perm("assessments.add_question")
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.change_question"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.assessment
            )
        )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.delete_question"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.assessment
            )
        )


# ==========================================================
# ANSWER OPTION MANAGEMENT
# ==========================================================

@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("option_text", "question", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("option_text", "question__question_text")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company = get_company_for_user(request.user)

        if company is None:
            return qs.none()

        return qs.filter(
            question__assessment__internship__company=company
        )

    def has_module_permission(self, request):
        return (
            request.user.is_superuser
            or request.user.has_perm("assessments.view_answeroption")
            or request.user.has_perm("assessments.add_answeroption")
        )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.view_answeroption"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.question.assessment
            )
        )

    def has_add_permission(self, request):
        return (
            request.user.is_superuser
            or request.user.has_perm("assessments.add_answeroption")
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.change_answeroption"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.question.assessment
            )
        )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.delete_answeroption"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.question.assessment
            )
        )


# ==========================================================
# STUDENT RESPONSES (READ ONLY)
# ==========================================================

class StudentResponseInline(admin.TabularInline):
    model = StudentResponse
    extra = 0
    can_delete = False
    fields = (
        "question",
        "selected_option",
        "text_answer",
        "marks_awarded",
        "saved_at",
    )
    readonly_fields = fields


# ==========================================================
# ASSESSMENT ATTEMPTS
# ==========================================================

@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "started_at",
        "submitted_at",
        "score",
        "total_marks",
        "percentage",
        "status",
    )

    list_filter = ("status",)
    inlines = [StudentResponseInline]

    readonly_fields = (
        "assignment",
        "started_at",
        "submitted_at",
        "score",
        "total_marks",
        "percentage",
        "status",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company = get_company_for_user(request.user)

        if company is None:
            return qs.none()

        return qs.filter(
            assignment__assessment__internship__company=company
        )

    def has_add_permission(self, request):
        # Attempts are created through the examination engine.
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.is_authenticated:
            return False

        if not request.user.groups.filter(
            name="Company Permissions"
        ).exists():
            return False

        company = get_company_for_user(request.user)

        if company is None:
            return False

        # Django calls this with obj=None for the changelist.
        if obj is None:
            return True

        return (
            obj.assignment.assessment.internship.company_id
            == company.pk
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm(
            "assessments.view_assessment_results"
        ):
            return False

        company = get_company_for_user(request.user)

        if company is None:
            return False

        if obj is None:
            return True

        return (
            obj.assignment.assessment.internship.company_id
            == company.pk
        )


# ==========================================================
# ASSESSMENT ASSIGNMENTS
# ==========================================================

@admin.register(AssessmentAssignment)
class AssessmentAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "assessment",
        "application",
        "assigned_at",
        "status",
    )
    list_filter = ("status", "assessment")
    search_fields = ("assessment__title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        company = get_company_for_user(request.user)

        if company is None:
            return qs.none()

        return qs.filter(assessment__internship__company=company)

    def has_add_permission(self, request):
        return (
            request.user.is_superuser
            or request.user.has_perm("assessments.assign_assessment")
        )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.view_assessment"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.assessment
            )
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.assign_assessment"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.assessment
            )
        )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if not request.user.has_perm("assessments.assign_assessment"):
            return False

        return (
            obj is None
            or assessment_is_owned_by_user(
                request.user, obj.assessment
            )
        )