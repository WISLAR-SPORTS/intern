
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from internships.models import Application
from students.models import Student

from .models import (
    AnswerOption,
    Assessment,
    AssessmentAssignment,
    AssessmentAttempt,
    Question,
    StudentResponse,
)


def get_current_student(user):
    try:
        return Student.objects.get(user=user)
    except Student.DoesNotExist:
        return None


def get_eligible_assignment(user, assessment):
    """Return the assignment associated with a shortlisted application."""
    student = get_current_student(user)

    if student is None:
        return None

    application = Application.objects.filter(
        student=student,
        internship=assessment.internship,
        status="shortlisted",
    ).first()

    if application is None:
        return None

    return AssessmentAssignment.objects.filter(
        assessment=assessment,
        application=application,
    ).first()


def attempt_deadline(attempt):
    """Return the earlier of the duration limit and assessment closing time."""
    assessment = attempt.assignment.assessment

    duration_end = attempt.started_at + timedelta(
        minutes=assessment.duration_minutes
    )

    return min(duration_end, assessment.closes_at)


from decimal import Decimal

from django.db import transaction
from django.utils import timezone


@transaction.atomic
def finish_attempt(attempt):
    """
    Finalize an attempt, calculate its score, and accept a
    shortlisted applicant if the submitted assessment is passed.

    Call this after locking the attempt with select_for_update().
    """

    if attempt.status != "in_progress":
        return attempt

    now = timezone.now()
    deadline = attempt_deadline(attempt)

    if now < deadline:
        attempt.status = "submitted"
        attempt.submitted_at = now
    else:
        attempt.status = "expired"
        attempt.submitted_at = deadline

    assignment = attempt.assignment
    assessment = assignment.assessment

    questions = assessment.questions.prefetch_related("options")

    score = Decimal("0.00")
    total = Decimal("0.00")

    responses = {
        response.question_id: response
        for response in attempt.responses.all()
    }

    response_updates = []

    for question in questions:
        total += question.marks

        response = responses.get(question.pk)
        awarded = Decimal("0.00")

        if response and response.selected_option_id:
            if question.options.filter(
                pk=response.selected_option_id,
                is_correct=True,
            ).exists():
                awarded = question.marks

        if response:
            response.marks_awarded = awarded
            response_updates.append(response)

        score += awarded

    if response_updates:
        StudentResponse.objects.bulk_update(
            response_updates,
            ["marks_awarded"],
        )

    attempt.score = score
    attempt.total_marks = total
    attempt.percentage = (
        (score * Decimal("100") / total).quantize(
            Decimal("0.01")
        )
        if total > 0
        else Decimal("0.00")
    )

    # Save the finalized attempt first.
    attempt.save(
        update_fields=[
            "status",
            "submitted_at",
            "score",
            "total_marks",
            "percentage",
        ]
    )

    assignment.status = (
        "expired"
        if attempt.status == "expired"
        else "submitted"
    )
    assignment.save(update_fields=["status"])

    # Automatically accept a qualifying shortlisted applicant.
    # Expired attempts do not qualify under this policy.
    if (
        attempt.status == "submitted"
        and attempt.percentage >= assessment.pass_mark
    ):
        application = (
            Application.objects
            .select_for_update()
            .get(pk=assignment.application_id)
        )

        if application.status == "shortlisted":
            application.status = "accepted"
            application.reviewed_at = timezone.now()

            application.save(
                update_fields=[
                    "status",
                    "reviewed_at",
                ]
            )

            # Notify the student about automatic acceptance.
            from students.models import Notification

            Notification.objects.create(
                student=application.student,
                notification_type="application",
                action="application_accepted",
                title="Congratulations! Your Application Has Been Accepted",
                message=(
                    f"Congratulations! You passed the assessment for "
                    f"{assessment.internship.title}, and your application "
                    f"has been accepted. You can view your application "
                    f"status from your student dashboard."
                ),
                application=application,
                internship=assessment.internship,
            )

    return attempt



def unavailable_response(request):
    return render(
        request,
        "assessments/unavailable.html",
        status=403,
    )


# =========================================================
# ASSESSMENT LIST
# =========================================================

@login_required
def assessment_list(request):
    student = get_current_student(request.user)

    if student is None:
        return render(
            request,
            "assessments/not_eligible.html",
            status=403,
        )

    applications = Application.objects.filter(
        student=student,
        status="shortlisted",
    ).select_related("internship")

    now = timezone.now()

    assessments = (
        Assessment.objects.filter(
            internship_id__in=applications.values("internship_id"),
            status="published",
            opens_at__lte=now,
            closes_at__gt=now,
        )
        .select_related("internship", "internship__company")
        .order_by("closes_at")
    )

    rows = []

    for assessment in assessments:
        application = applications.filter(
            internship_id=assessment.internship_id
        ).first()

        if application is None:
            continue

        assignment, _ = AssessmentAssignment.objects.get_or_create(
            assessment=assessment,
            application=application,
        )

        attempt = assignment.attempts.order_by(
            "-started_at"
        ).first()

        # Automatically finalize expired attempts.
        if (
            attempt
            and attempt.status == "in_progress"
            and now >= attempt_deadline(attempt)
        ):
            with transaction.atomic():
                locked_attempt = (
                    AssessmentAttempt.objects
                    .select_for_update()
                    .select_related("assignment__assessment")
                    .get(pk=attempt.pk)
                )

                finish_attempt(locked_attempt)
                attempt = locked_attempt

        rows.append(
            {
                "assessment": assessment,
                "assignment": assignment,
                "attempt": attempt,
            }
        )

    return render(
        request,
        "assessments/assessment_list.html",
        {"rows": rows},
    )


# =========================================================
# START ASSESSMENT
# =========================================================

@login_required
@transaction.atomic
def start_assessment(request, assessment_id):
    assessment = get_object_or_404(
        Assessment,
        pk=assessment_id,
        status="published",
    )

    now = timezone.now()

    if not (assessment.opens_at <= now < assessment.closes_at):
        return unavailable_response(request)

    student = get_current_student(request.user)

    if student is None:
        return render(
            request,
            "assessments/not_eligible.html",
            status=403,
        )

    application = Application.objects.filter(
        student=student,
        internship=assessment.internship,
        status="shortlisted",
    ).first()

    if application is None:
        return render(
            request,
            "assessments/not_eligible.html",
            status=403,
        )

    assignment, _ = AssessmentAssignment.objects.get_or_create(
        assessment=assessment,
        application=application,
    )

    # Lock the assignment before checking or creating an attempt.
    assignment = (
        AssessmentAssignment.objects
        .select_for_update()
        .select_related("assessment", "application")
        .get(pk=assignment.pk)
    )

    attempt = assignment.attempts.order_by("-started_at").first()

    if attempt and attempt.status == "in_progress":
        attempt = (
            AssessmentAttempt.objects
            .select_for_update()
            .select_related("assignment__assessment")
            .get(pk=attempt.pk)
        )

        if now >= attempt_deadline(attempt):
            finish_attempt(attempt)

            return redirect(
                "assessments:assessment_result",
                attempt_id=attempt.pk,
            )

        return redirect(
            "assessments:take_assessment",
            attempt_id=attempt.pk,
        )

    if assignment.attempts.count() >= assessment.max_attempts:
        return render(
            request,
            "assessments/attempt_limit.html",
            status=403,
        )

    attempt = AssessmentAttempt.objects.create(
        assignment=assignment,
    )

    assignment.status = "in_progress"
    assignment.save(update_fields=["status"])

    return redirect(
        "assessments:take_assessment",
        attempt_id=attempt.pk,
    )


# =========================================================
# TAKE ASSESSMENT
# =========================================================

@login_required
def take_assessment(request, attempt_id):
    student = get_current_student(request.user)

    if student is None:
        return render(
            request,
            "assessments/not_eligible.html",
            status=403,
        )

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assignment__assessment",
            "assignment__application",
        ),
        pk=attempt_id,
        assignment__application__student=student,
    )

    assessment = attempt.assignment.assessment

    if attempt.assignment.application.status != "shortlisted":
        return render(
            request,
            "assessments/not_eligible.html",
            status=403,
        )

    if attempt.status != "in_progress":
        return redirect(
            "assessments:assessment_result",
            attempt_id=attempt.pk,
        )

    if timezone.now() >= attempt_deadline(attempt):
        with transaction.atomic():
            locked_attempt = (
                AssessmentAttempt.objects
                .select_for_update()
                .select_related("assignment__assessment")
                .get(pk=attempt.pk)
            )

            finish_attempt(locked_attempt)

        return redirect(
            "assessments:assessment_result",
            attempt_id=attempt.pk,
        )

    questions = assessment.questions.prefetch_related("options")

    saved = {
        response.question_id: response.selected_option_id
        for response in attempt.responses.all()
    }

    # Never expose is_correct in the student-facing template.
    question_data = [
        {
            "question": question,
            "options": question.options.all(),
            "selected_option_id": saved.get(question.pk),
        }
        for question in questions
    ]

    return render(
        request,
        "assessments/take_assessment.html",
        {
            "attempt": attempt,
            "assessment": assessment,
            "question_data": question_data,
            "deadline_ms": int(
                attempt_deadline(attempt).timestamp() * 1000
            ),
        },
    )

import logging
import sqlite3

from django.contrib.auth.decorators import login_required
from django.db import OperationalError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
import time
import sqlite3

from django.db import OperationalError, transaction
from django.http import JsonResponse
from django.utils import timezone

def is_database_locked(exc):
    """Identify transient SQLite database-lock errors."""
    current = exc

    while current is not None:
        if isinstance(current, sqlite3.OperationalError):
            if "locked" in str(current).lower():
                return True

        current = current.__cause__

    return "database is locked" in str(exc).lower()


def retry_database_lock(operation, attempts=4):
    """
    Retry an operation only after a transient database-lock error.

    The operation must use its own transaction.atomic() block,
    so every retry starts with a fresh transaction.
    """
    for attempt_number in range(attempts):
        try:
            return operation()

        except OperationalError as exc:
            if not is_database_locked(exc):
                raise

            if attempt_number == attempts - 1:
                raise

            # 0.15, 0.30, then 0.60 seconds.
            time.sleep(0.15 * (2 ** attempt_number))


logger = logging.getLogger(__name__)
# =========================================================
# SAVE RESPONSE
# =========================================================

@login_required
@require_POST
def save_response(request, attempt_id):
    student = get_current_student(request.user)

    if student is None:
        return JsonResponse({"error": "Not eligible."}, status=403)

    question_id = request.POST.get("question_id")
    option_id = request.POST.get("option_id")

    if not question_id or not option_id:
        return JsonResponse(
            {"error": "A question and answer option are required."},
            status=400,
        )

    def save_once():
        with transaction.atomic():
            attempt = get_object_or_404(
                AssessmentAttempt.objects.select_related(
                    "assignment__assessment",
                    "assignment__application",
                ).select_for_update(),
                pk=attempt_id,
                assignment__application__student=student,
            )

            if attempt.status != "in_progress":
                return JsonResponse(
                    {"error": "This attempt has already ended."},
                    status=400,
                )

            if attempt.assignment.application.status != "shortlisted":
                return JsonResponse(
                    {"error": "You are no longer eligible for this assessment."},
                    status=403,
                )

            if timezone.now() >= attempt_deadline(attempt):
                finish_attempt(attempt)
                return JsonResponse(
                    {"error": "The assessment deadline has passed."},
                    status=400,
                )

            question = get_object_or_404(
                Question,
                pk=question_id,
                assessment_id=attempt.assignment.assessment_id,
            )

            option = get_object_or_404(
                AnswerOption,
                pk=option_id,
                question_id=question.pk,
            )

            StudentResponse.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "selected_option": option,
                    "text_answer": "",
                },
            )

        return JsonResponse({"saved": True})

    try:
        return retry_database_lock(save_once)

    except OperationalError as exc:
        if is_database_locked(exc):
            logger.warning(
                "Database remained locked after retries while saving "
                "attempt %s, question %s.",
                attempt_id,
                question_id,
            )

            return JsonResponse(
                {
                    "error": (
                        "Your answer could not be saved because the "
                        "database is busy. Please retry."
                    ),
                    "retry": True,
                },
                status=503,
            )

        raise

# =========================================================
# SUBMIT ASSESSMENT
# =========================================================

@login_required
@require_POST
def submit_assessment(request, attempt_id):
    student = get_current_student(request.user)

    if student is None:
        return JsonResponse({"error": "Not eligible."}, status=403)

    def submit_once():
        with transaction.atomic():
            attempt = get_object_or_404(
                AssessmentAttempt.objects.select_for_update().select_related(
                    "assignment__assessment",
                    "assignment__application",
                ),
                pk=attempt_id,
                assignment__application__student=student,
            )

            if attempt.status == "in_progress":
                if (
                    attempt.assignment.application.status
                    != "shortlisted"
                ):
                    return JsonResponse(
                        {
                            "error": (
                                "You are no longer eligible "
                                "for this assessment."
                            )
                        },
                        status=403,
                    )

                finish_attempt(attempt)

            return JsonResponse(
                {
                    "submitted": True,
                    "status": attempt.status,
                    "redirect_url": reverse(
                        "assessments:assessment_result",
                        kwargs={"attempt_id": attempt.pk},
                    ),
                }
            )

    try:
        return retry_database_lock(submit_once)

    except OperationalError as exc:
        if is_database_locked(exc):
            logger.exception(
                "Database remained locked while submitting attempt %s.",
                attempt_id,
            )

            return JsonResponse(
                {
                    "error": (
                        "The database is busy. Your submission "
                        "could not be confirmed. Please retry."
                    ),
                    "retry": True,
                },
                status=503,
            )

        raise



# =========================================================
# ASSESSMENT RESULT
# =========================================================

@login_required
def assessment_result(request, attempt_id):
    student = get_current_student(request.user)

    if student is None:
        return render(
            request,
            "assessments/not_eligible.html",
            status=403,
        )

    attempt = get_object_or_404(
        AssessmentAttempt.objects.select_related(
            "assignment__assessment",
            "assignment__application",
        ),
        pk=attempt_id,
        assignment__application__student=student,
    )

    if attempt.status == "in_progress":
        if timezone.now() >= attempt_deadline(attempt):
            with transaction.atomic():
                locked_attempt = (
                    AssessmentAttempt.objects
                    .select_for_update()
                    .select_related("assignment__assessment")
                    .get(pk=attempt.pk)
                )

                finish_attempt(locked_attempt)

            attempt.refresh_from_db()
        else:
            return redirect(
                "assessments:take_assessment",
                attempt_id=attempt.pk,
            )

    assessment = attempt.assignment.assessment

    return render(
        request,
        "assessments/assessment_result.html",
        {
            "attempt": attempt,
            "show_results": assessment.show_results,
        },
    )
