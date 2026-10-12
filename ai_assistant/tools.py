from django.db.models import Q

from internships.models import (
    Internship,
    Application,
    
)
from students.models import Student
from django.db.models import Q
from django.utils import timezone
def search_internships(
    user,
    field=None,
    location=None,
    skill=None,
):
    """
    Search active, non-expired internships.

    Supports flexible matching across internship titles,
    descriptions, company names, types, and custom fields.

    Field and skill are combined using OR so that an
    internship can match either criterion. An explicitly
    supplied location remains a required filter.
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
    # ACTIVE AND NON-EXPIRED INTERNSHIPS
    # ==================================================

    today = timezone.localdate()

    queryset = (
        Internship.objects
        .filter(active=True)
        .filter(
            Q(deadline__isnull=True)
            | Q(deadline__gte=today)
        )
        .select_related("company")
        .prefetch_related("custom_fields")
    )

    # ==================================================
    # FLEXIBLE FIELD AND SKILL SEARCH
    # ==================================================

    search_terms = []

    for term in (field, skill):
        if term:
            term = term.strip()

            if term and term.casefold() not in {
                existing.casefold()
                for existing in search_terms
            }:
                search_terms.append(term)

    if search_terms:
        search_query = Q()

        for term in search_terms:
            term_query = (
                Q(title__icontains=term)
                | Q(description__icontains=term)
                | Q(internship_type__icontains=term)
                | Q(
                    company__company_name__icontains=term
                )
                | Q(custom_fields__label__icontains=term)
                | Q(custom_fields__options__icontains=term)
            )

            search_query |= term_query

        queryset = queryset.filter(search_query)

    # ==================================================
    # LOCATION FILTER
    #
    # Only filter by location when explicitly supplied.
    # ==================================================

    if location and location.strip():
        queryset = queryset.filter(
            location__icontains=location.strip()
        )

    # ==================================================
    # REMOVE DUPLICATES AND LIMIT DATABASE RESULTS
    # ==================================================

    internships = list(
        queryset
        .distinct()
        .order_by("-created_at")[:100]
    )

    # ==================================================
    # RANK RESULTS BY RELEVANCE
    # ==================================================

    def relevance_score(internship):
        score = 0

        title = (internship.title or "").casefold()
        description = (
            internship.description or ""
        ).casefold()
        internship_type = (
            internship.internship_type or ""
        ).casefold()
        company_name = (
            internship.company.company_name
            if internship.company
            else ""
        ).casefold()

        custom_text = " ".join(
            str(value or "")
            for custom_field in internship.custom_fields.all()
            for value in (
                custom_field.label,
                custom_field.options,
            )
        ).casefold()

        searchable_text = " ".join(
            (
                title,
                description,
                internship_type,
                company_name,
                custom_text,
            )
        )

        for term in search_terms:
            term = term.casefold()

            if term == title:
                score += 10
            elif term in title:
                score += 6

            if term in description:
                score += 3

            if term in internship_type:
                score += 3

            if term in company_name:
                score += 2

            if term in custom_text:
                score += 2

            # Small bonus for related words that match
            # independently. This helps broader searches.
            words = [
                word
                for word in term.split()
                if len(word) > 2
            ]

            for word in words:
                if word in searchable_text:
                    score += 1

        return score

    internships.sort(
        key=lambda internship: (
            relevance_score(internship),
            internship.created_at,
        ),
        reverse=True,
    )

    # ==================================================
    # BUILD RESPONSE
    # ==================================================

    results = []

    for internship in internships[:20]:
        custom_fields = [
            {
                "id": custom_field.id,
                "label": custom_field.label,
                "field_type": custom_field.field_type,
                "required": custom_field.required,
                "options": custom_field.options,
                "order": custom_field.order,
            }
            for custom_field in internship.custom_fields.all()
        ]

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



from django.db.models import Q
from django.utils import timezone


def get_internship_details(user, internship_id):
    """
    Get detailed information about an active,
    non-expired internship.
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
    # FIND ACTIVE, NON-EXPIRED INTERNSHIP
    # ==================================================

    today = timezone.localdate()

    internship = (
        Internship.objects
        .filter(
            id=internship_id,
            active=True,
        )
        .filter(
            Q(deadline__isnull=True)
            | Q(deadline__gte=today)
        )
        .select_related("company")
        .prefetch_related("custom_fields")
        .first()
    )

    if internship is None:
        return {
            "error": (
                "Internship not found, expired, "
                "or no longer active."
            )
        }

    # ==================================================
    # CUSTOM FIELDS
    # ==================================================

    custom_fields = [
        {
            "id": custom_field.id,
            "label": custom_field.label,
            "field_type": custom_field.field_type,
            "required": custom_field.required,
            "options": custom_field.options,
            "order": custom_field.order,
        }
        for custom_field in internship.custom_fields.all()
    ]

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
        "internship_type": internship.internship_type,
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
        "company": application.internship.company.company_name,
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
def get_my_profile(user):
    """
    Retrieve the authenticated student's profile.
    """

    if not user.is_authenticated:
        raise PermissionError(
            "Authentication required."
        )

    if user.role != "student":
        raise PermissionError(
            "Student account required."
        )

    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return {
            "error": "Student profile not found."
        }

    # Read actual fields available on the Student model.
    profile = {}

    for field in student._meta.concrete_fields:
        if field.name == "user":
            continue

        value = getattr(student, field.name, None)

        if value is None:
            profile[field.name] = None
        elif hasattr(value, "isoformat"):
            profile[field.name] = value.isoformat()
        elif isinstance(value, (str, int, float, bool)):
            profile[field.name] = value
        else:
            profile[field.name] = str(value)

    # Include relevant information from the user account.
    profile["email"] = user.email
    profile["username"] = user.get_username()

    return profile