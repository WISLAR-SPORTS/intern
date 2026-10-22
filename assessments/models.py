

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from internships.models import Internship, Application


class Assessment(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("closed", "Closed"),
    ]

    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    pass_mark = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Required percentage to pass.",
    )
    max_attempts = models.PositiveIntegerField(default=1)
    show_results = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_assessments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("assign_assessment", "Can assign assessments to applicants"),
            ("view_assessment_results", "Can view assessment results"),
            ("publish_assessment", "Can publish assessments"),
        ]

    def clean(self):
        super().clean()

        if self.opens_at and self.closes_at:
            if self.closes_at <= self.opens_at:
                raise ValidationError(
                    {"closes_at": "Closing time must be after opening time."}
                )

        if self.internship_id and self.pk:
            # Once attempts exist, avoid changing the exam's
            # structure or schedule without a controlled workflow.
            if self.assignments.filter(attempts__isnull=False).exists():
                original = Assessment.objects.get(pk=self.pk)
                protected = [
                    "internship_id",
                    "duration_minutes",
                    "opens_at",
                    "closes_at",
                ]
                if any(
                    getattr(original, field) != getattr(self, field)
                    for field in protected
                ):
                    raise ValidationError(
                        "The assessment schedule cannot be changed "
                        "after an attempt has been created."
                    )

    @property
    def company(self):
        return self.internship.company

    def __str__(self):
        return self.title


class Question(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.TextField()
    marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "order"],
                name="unique_assessment_question_order",
            )
        ]

    def __str__(self):
        return f"{self.assessment.title}: Question {self.order}"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
    )
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


class AssessmentAssignment(models.Model):
    STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("expired", "Expired"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="assessment_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="assigned",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "application"],
                name="unique_assessment_application_assignment",
            )
        ]

    def clean(self):
        super().clean()
        if self.assessment_id and self.application_id:
            if (
                self.assessment.internship_id
                != self.application.internship_id
            ):
                raise ValidationError(
                    "The application must belong to the assessment's internship."
                )

    def __str__(self):
        return f"{self.application} - {self.assessment}"


class AssessmentAttempt(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("submitted", "Submitted"),
        ("expired", "Expired"),
    ]

    assignment = models.ForeignKey(
        AssessmentAssignment,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    total_marks = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    percentage = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment"],
                condition=models.Q(status="in_progress"),
                name="one_active_attempt_per_assignment",
            )
        ]

    def __str__(self):
        return f"Attempt {self.pk} - {self.assignment}"


class StudentResponse(models.Model):
    attempt = models.ForeignKey(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_responses",
    )
    text_answer = models.TextField(blank=True)
    marks_awarded = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_attempt_question_response",
            )
        ]

    def clean(self):
        super().clean()

        if self.attempt_id and self.question_id:
            if (
                self.attempt.assignment.assessment_id
                != self.question.assessment_id
            ):
                raise ValidationError(
                    "The question does not belong to this assessment."
                )

        if self.selected_option_id and self.question_id:
            if self.selected_option.question_id != self.question_id:
                raise ValidationError(
                    "The selected option does not belong to this question."
                )

    def __str__(self):
        return f"Response {self.pk}"