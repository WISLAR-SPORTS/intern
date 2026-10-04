from django.db.models import Q

from internships.models import (
    Internship,
    Application,
    
)
from students.models import Student

def get_my_profile(user):
    """
    Return information the AI needs about
    the authenticated student.
    """

    # ==================================================
    # AUTHENTICATION
    # ==================================================

    if not user.is_authenticated:
        raise PermissionError(
            "Authentication required."
        )

    # ==================================================
    # ROLE CHECK
    # ==================================================

    if user.role != "student":
        raise PermissionError(
            "Student account required."
        )

    # ==================================================
    # STUDENT PROFILE
    # ==================================================

    try:
        student = user.student
    except Student.DoesNotExist:
        raise PermissionError(
            "No student profile is associated "
            "with this account."
        )

    # ==================================================
    # RETURN PROFILE
    # ==================================================

    return {
        # ----------------------------------------------
        # Information from User model
        # ----------------------------------------------

        "user_id": user.id,
        "name": user.get_full_name(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,

        # ----------------------------------------------
        # Information from Student model
        # ----------------------------------------------

        "student_id": student.id,

        "university": (
            student.university.name
            if student.university
            else None
        ),

        "registration_number": (
            student.registration_number
        ),

        "course": student.course,

        "year_of_study": (
            student.year_of_study
        ),

        "phone": student.phone,

        "skills": student.skills or "",

        "profile_picture": (
            student.profile_picture.url
            if student.profile_picture
            else None
        ),
    }

from django.db.models import Q

from internships.models import (
    Internship,
    Application,
)

from django.db.models import Q

from internships.models import Internship


def search_internships(
    user,
    field=None,
    location=None,
    skill=None,
):
    """
    Search active internships.

    Uses the actual fields available
    in the Internship model.
    """

    # ==================================================
    # AUTHENTICATION
    # ==================================================

    if not user.is_authenticated:
        raise PermissionError(
            "Authentication required."
        )

    # ==================================================
    # ROLE CHECK
    # ==================================================

    if user.role != "student":
        raise PermissionError(
            "Student account required."
        )

    # ==================================================
    # START WITH ACTIVE INTERNSHIPS
    # ==================================================

    queryset = (
        Internship.objects
        .filter(active=True)
        .select_related("company")
        .prefetch_related("custom_fields")
    )

    # ==================================================
    # SEARCH FIELD
    # ==================================================

    if field:

        queryset = queryset.filter(
            Q(title__icontains=field)
            | Q(description__icontains=field)
            | Q(internship_type__icontains=field)
            | Q(custom_fields__label__icontains=field)
            | Q(custom_fields__options__icontains=field)
        )

    # ==================================================
    # LOCATION
    # ==================================================

    if location:

        queryset = queryset.filter(
            location__icontains=location
        )

    # ==================================================
    # SKILL
    #
    # Search description, custom field labels
    # and custom field options.
    # ==================================================

    if skill:

        queryset = queryset.filter(
            Q(description__icontains=skill)
            | Q(title__icontains=skill)
            | Q(custom_fields__label__icontains=skill)
            | Q(custom_fields__options__icontains=skill)
        )

    # ==================================================
    # REMOVE DUPLICATES
    #
    # A single internship can have multiple matching
    # custom fields.
    # ==================================================

    internships = (
        queryset
        .distinct()
        .order_by("-created_at")[:20]
    )

    results = []

    # ==================================================
    # BUILD AI RESPONSE
    # ==================================================

    for internship in internships:

        custom_fields = []

        for custom_field in internship.custom_fields.all():

            custom_fields.append(
                {
                    "id": custom_field.id,

                    "label": custom_field.label,

                    "field_type": (
                        custom_field.field_type
                    ),

                    "required": (
                        custom_field.required
                    ),

                    "options": (
                        custom_field.options
                    ),

                    "order": (
                        custom_field.order
                    ),
                }
            )

        results.append(
            {
                "id": internship.id,

                "title": internship.title,

                "company": (
                    internship.company.company_name
                    if internship.company
                    else None
                ),

                "location": internship.location,

                "internship_type": (
                    internship.internship_type
                ),

                "description": internship.description,

                "custom_fields": custom_fields,

                "deadline": (
                    internship.deadline.isoformat()
                    if internship.deadline
                    else None
                ),
            }
        )

    return results
def get_internship_details(
    user,
    internship_id,
):
    """
    Get detailed information about
    one active internship.
    """

    # ==================================================
    # AUTHENTICATION
    # ==================================================

    if not user.is_authenticated:
        raise PermissionError(
            "Authentication required."
        )

    # ==================================================
    # ROLE CHECK
    # ==================================================

    if user.role != "student":
        raise PermissionError(
            "Student account required."
        )

    # ==================================================
    # FIND INTERNSHIP
    # ==================================================

    try:

        internship = (
            Internship.objects
            .select_related("company")
            .prefetch_related("custom_fields")
            .get(
                id=internship_id,
                active=True,
            )
        )

    except Internship.DoesNotExist:

        return {
            "error": (
                "Internship not found or "
                "is no longer active."
            )
        }

    # ==================================================
    # CUSTOM FIELDS
    # ==================================================

    custom_fields = []

    for custom_field in internship.custom_fields.all():

        custom_fields.append(
            {
                "id": custom_field.id,

                "label": custom_field.label,

                "field_type": (
                    custom_field.field_type
                ),

                "required": (
                    custom_field.required
                ),

                "options": (
                    custom_field.options
                ),

                "order": (
                    custom_field.order
                ),
            }
        )

    # ==================================================
    # RETURN DETAILS
    # ==================================================

    return {
        "id": internship.id,

        "title": internship.title,

        "company": (
            internship.company.company_name
            if internship.company
            else None
        ),

        "description": internship.description,

        "location": internship.location,

        "internship_type": (
            internship.internship_type
        ),

        "custom_fields": custom_fields,

        "deadline": (
            internship.deadline.isoformat()
            if internship.deadline
            else None
        ),
    }


def get_my_applications(user):
    if not user.is_authenticated:
        raise PermissionError("Authentication required.")

    if user.role != "student":
        raise PermissionError("Student account required.")

    applications = (
        Application.objects
        .filter(student=user.student)
        .select_related(
            "internship",
            "internship__company",
        )
    )

    results = []

    for application in applications:
        results.append(
            {
                "application_id": application.id,
                "internship": application.internship.title,
                "company": application.internship.company.company_name,

                "status": application.status,
                "applied_date": (
                    application.applied_date.isoformat()
                    if application.applied_date
                    else None
                ),
            }
        )

    return results
def get_application_status(
    user,
    application_id,
):
    if not user.is_authenticated:
        raise PermissionError("Authentication required.")

    if user.role != "student":
        raise PermissionError("Student account required.")

    application = Application.objects.get(
        id=application_id,
        student=user.student,
    )

    return {
        "application_id": application.id,
        "internship": application.internship.title,
        "company": application.internship.company.company_namename,
        "status": application.status,
        "applied_date": (
            application.applied_date.isoformat()
            if application.applied_date
            else None
        ),
    }
from urllib.parse import quote


def get_learning_resource(student, topic, level="beginner"):
    """
    Generate a YouTube learning resource for any topic
    requested by the authenticated student.
    """

    if not topic or not topic.strip():
        return {
            "success": False,
            "message": "Please provide a learning topic."
        }

    topic = topic.strip()

    search_query = (
        f"{topic} {level} tutorial course lessons"
    )

    youtube_url = (
        "https://www.youtube.com/results?search_query="
        + quote(search_query)
    )

    return {
        "success": True,
        "topic": topic,
        "level": level,
        "platform": "YouTube",
        "url": youtube_url,
        "message": (
            f"YouTube learning resources found "
            f"for {topic}."
        ),
    }
