from django.contrib import admin
from .models import Internship, InternshipField, Application, ApplicationAnswer


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
    )

    inlines = [
        InternshipFieldInline,
    ]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "internship",
        "status",
        "score",
        "applied_date",
        "reviewed_at",
    )

    list_filter = (
        "status",
        "applied_date",
    )

    search_fields = (
        "student__user__username",
        "student__user__first_name",
        "student__user__last_name",
        "student__registration_number",
        "internship__title",
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
