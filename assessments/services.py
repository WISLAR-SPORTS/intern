
from django.db import transaction
from django.utils import timezone

from internships.models import Application


@transaction.atomic
def update_application_from_assessment(attempt):
    """
    Accept a shortlisted application if the finalized assessment
    meets or exceeds the assessment's configured pass mark.
    """

    # Only process finalized, submitted attempts.
    if attempt.status != "submitted" or not attempt.submitted_at:
        return False

    assignment = attempt.assignment
    assessment = assignment.assessment

    # Compare the actual percentage with the configured pass mark.
    if attempt.percentage < assessment.pass_mark:
        return False

    # Lock the associated application before changing its status.
    application = (
        Application.objects
        .select_for_update()
        .get(pk=assignment.application_id)
    )

    # Only shortlisted applications qualify for automatic acceptance.
    if application.status != "shortlisted":
        return False

    application.status = "accepted"
    application.reviewed_at = timezone.now()

    application.save(
        update_fields=["status", "reviewed_at"]
    )

    return True