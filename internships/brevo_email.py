
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_shortlist_email(application):
    """
    Send a shortlist notification to the student using Brevo.
    Returns True if Brevo accepts the email; otherwise False.
    """

    student = application.student
    user = student.user

    recipient_email = (user.email or "").strip()

    if not recipient_email:
        logger.warning(
            "Cannot send shortlist email for application %s: "
            "student has no email address.",
            application.pk,
        )
        return False

    api_key = getattr(settings, "BREVO_API_KEY", None)
    sender_email = getattr(
        settings, "BREVO_SENDER_EMAIL", None
    )
    sender_name = getattr(
        settings,
        "BREVO_SENDER_NAME",
        "Internship Management System",
    )

    if not api_key or not sender_email:
        logger.error(
            "Brevo email settings are missing."
        )
        return False

    student_name = (
        user.get_full_name().strip()
        or user.username
        or "Student"
    )

    internship_title = application.internship.title

    subject = "Congratulations! You Have Been Shortlisted"

    text_content = (
        f"Dear {student_name},\n\n"
        f"Congratulations! Your application for "
        f"{internship_title} has been shortlisted "
        f"for an interview.\n\n"
        "Please log in to your student account to check "
        "for further updates and interview details.\n\n"
        "Best regards,\n"
        f"{sender_name}"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
    </head>
    <body style="margin:0; padding:24px;
                 background-color:#f4f6f9;
                 font-family:Arial,sans-serif;
                 color:#243047;">

        <div style="max-width:600px; margin:0 auto;
                    background:#ffffff; border-radius:12px;
                    padding:32px;">

            <h1 style="color:#16803c; font-size:24px;">
                Congratulations, {student_name}!
            </h1>

            <p style="font-size:16px; line-height:1.7;">
                Your application for
                <strong>{internship_title}</strong>
                has been shortlisted for an interview.
            </p>

            <p style="font-size:16px; line-height:1.7;">
                This is an important step in the selection
                process. Please log in to your student
                account to check for further updates and
                interview details.
            </p>

            <p style="font-size:15px; line-height:1.7;">
                Best regards,<br>
                <strong>{sender_name}</strong>
            </p>

        </div>
    </body>
    </html>
    """

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient_email,
                "name": student_name,
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        logger.info(
            "Shortlist email accepted by Brevo for "
            "application %s.",
            application.pk,
        )
        return True

    except requests.RequestException:
        logger.exception(
            "Failed to send shortlist email for application %s.",
            application.pk,
        )
        return False
