from django.db import models
from companies.models import Company
from students.models import Student


class Internship(models.Model):

    JOB_TYPES = (

        ("fulltime", "Full Time"),
        ("parttime", "Part Time"),
        ("remote", "Remote"),

    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="internships"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()


    location = models.CharField(
        max_length=200,
        blank=True
    )


    internship_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES
    )


    deadline = models.DateField()


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    active = models.BooleanField(
        default=True
    )


    def __str__(self):
        return self.title



# Companies create their own internship questions here
class InternshipField(models.Model):

    FIELD_TYPES = (

        ("text", "Text"),
        ("textarea", "Log Text"),
        ("number", "Number"),
        ("email", "Email"),
        ("url", "Website URL"),
        ("date", "Date"),
        ("file", "File Upload"),
        ("checkbox", "Checkbox"),
        ("select", "Dropdown"),

    )


    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name="custom_fields"
    )


    label = models.CharField(
        max_length=200
    )


    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPES
    )


    required = models.BooleanField(
        default=True
    )
    options=models.TextField(blank=True, help_text="For dopdown fields, separate options with commas.")


    order = models.PositiveIntegerField(
        default=0
    )


    def __str__(self):
        return f"{self.internship.title} - {self.label}"

class Application(models.Model):

    STATUS = (
        ("pending", "Pending"),
        ("shortlisted", "Shortlisted"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    cover_letter = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    # ==========================================
    # COMPANY REVIEW
    # ==========================================

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    reviewer_notes = models.TextField(
        blank=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    applied_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "internship"],
                name="unique_student_internship_application"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.internship}"


# Stores answers to company-created fields
class ApplicationAnswer(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    field = models.ForeignKey(
        InternshipField,
        on_delete=models.CASCADE
    )

    answer = models.TextField(
        blank=True
    )

    file = models.FileField(
        upload_to="application_files/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.field.label}: {self.answer}"
