# students/admin.py

from django.contrib import admin
from .models import University, StudentVerified, Student


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "website",
        "verified",
    )
    list_filter = ("verified",)
    search_fields = (
        "name",
        "user__username",
        "user__email",
    )
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import path

from .models import University, StudentVerified, Student
from .forms import StudentVerifiedUploadForm
from .services import parse_excel


@admin.register(StudentVerified)
class StudentVerifiedAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "registration_number",
        "university",
        "created_at",
    )

    list_filter = (
        "university",
    )

    search_fields = (
        "full_name",
        "registration_number",
        "university__name",
    )

    change_list_template = (
        "admin/students/studentverified/change_list.html"
    )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(
                    self.upload_students
                ),
                name="students_studentverified_upload",
            ),
        ]

        return custom_urls + urls

    def upload_students(self, request):

        if request.method == "POST":

            form = StudentVerifiedUploadForm(
                request.POST,
                request.FILES,
            )

            if form.is_valid():

                uploaded_file = form.cleaned_data["file"]

                try:
                    students = parse_excel(uploaded_file)

                    university = request.user.university

                    existing_numbers = set(
                        StudentVerified.objects.filter(
                            university=university,
                            registration_number__in=[
                                student["registration_number"]
                                for student in students
                            ],
                        ).values_list(
                            "registration_number",
                            flat=True,
                        )
                    )

                    if existing_numbers:
                        raise ValidationError(
                            "These student numbers already exist: "
                            + ", ".join(existing_numbers)
                        )

                    with transaction.atomic():

                        StudentVerified.objects.bulk_create(
                            [
                                StudentVerified(
                                    university=university,
                                    registration_number=student[
                                        "registration_number"
                                    ],
                                    full_name=student[
                                        "full_name"
                                    ],
                                )
                                for student in students
                            ]
                        )

                    self.message_user(
                        request,
                        f"{len(students)} students imported successfully.",
                        messages.SUCCESS,
                    )

                    return redirect(
                        "admin:students_studentverified_changelist"
                    )

                except ValidationError as e:

                    form.add_error(
                        "file",
                        str(e),
                    )

        else:
            form = StudentVerifiedUploadForm()

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "title": "Upload Verified Students",
        }

        return render(
            request,
            "admin/students/studentverified/upload.html",
            context,
        )



@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "university",
        "registration_number",
        "course",
        "year_of_study",
        "phone",
    )
    list_filter = (
        "university",
        "year_of_study",
        "course",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "registration_number",
        "course",
    )
# notifications/admin.py

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "notification_type",
        "action",
        "title",
        "is_read",
        "is_deleted",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "action",
        "is_read",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "student__user__username",
        "student__user__email",
        "student__registration_number",
        "title",
        "message",
    )

    readonly_fields = ("created_at",)
