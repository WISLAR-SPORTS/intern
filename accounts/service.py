from django.contrib.auth import authenticate, get_user_model
from django.db import transaction

from companies.models import Company
from students.models import Student,  StudentVerified
from django.contrib.auth import authenticate, get_user_model
from companies.models import Company
from students.models import University


User = get_user_model()


# =====================================================
# USER
# =====================================================

def get_user_by_email(email):
    """
    Find a user using their email address.
    """

    try:
        return User.objects.get(
            email__iexact=email
        )
    except User.DoesNotExist:
        return None


# =====================================================
# AUTHENTICATION
# =====================================================

def authenticate_user(email, password):
    """
    Authenticate a user using their email and password.

    Django's default ModelBackend authenticates using
    the USERNAME_FIELD. If your User model still uses
    username as USERNAME_FIELD, we first get the user
    by email and then authenticate using username.
    """

    user = get_user_by_email(email)

    if user is None:
        return None

    return authenticate(
        username=user.username,
        password=password,
    )


# =====================================================
# ACCOUNT VALIDATION
# =====================================================

def validate_user_account(user):
    """
    Validate additional requirements for the user's role.

    Returns:
        None if valid
        Error message if invalid
    """

    if user.role == "company":

        try:
            company = user.company

        except Company.DoesNotExist:
            return "Company account was not found."

        if not company.verified:
            return (
                "Your company account has not been "
                "verified yet."
            )

    elif user.role == "university":

        try:
            university = user.university

        except University.DoesNotExist:
            return "University account was not found."

        if not university.verified:
            return (
                "Your university account has not been "
                "verified yet."
            )

    return None


# =====================================================
# ROLES
# =====================================================

def get_user_role(user):
    return user.role


def is_student(user):
    return user.role == "student"


def is_company(user):
    return user.role == "company"


def is_university(user):
    return user.role == "university"


def is_admin(user):
    return (
        user.role == "admin"
        or user.is_superuser
    )


# =====================================================
# LOGIN REDIRECT
# =====================================================

def get_login_redirect(user):

    if user.is_superuser:
        return "/admin/"

    if user.role == "student":
        return "student-dashboard"

    if user.role == "company":
        return "/admin/"

    if user.role == "university":
        return "/admin/"

    if user.role == "admin":
        return "/admin/"

    return "login"


# =====================================================
# STUDENT REGISTRATION
# =====================================================




@transaction.atomic
def register_student(data):
    university = data["university"]
    registration_number = data[
        "registration_number"
    ]

    verified_student = StudentVerified.objects.filter(
        university=university,
        registration_number=registration_number,
    ).first()

    if not verified_student:
        raise ValueError(
            "Your registration number was not found "
            "in the selected university's verified "
            "student list."
        )

    if Student.objects.filter(
        university=university,
        registration_number=registration_number,
    ).exists():
        raise ValueError(
            "A student account already exists for "
            "this registration number."
        )

    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        role="student",
        is_active=True,
    )

    student = Student.objects.create(
        user=user,
        university=university,
        registration_number=registration_number,
    
    
        
    )

    return user



# =====================================================
# COMPANY REGISTRATION
# =====================================================

@transaction.atomic
def register_company(data):

    user = User.objects.create_user(

        username=data["username"],

        email=data["email"],

        password=data["password"],

        role="company",

        is_active=True,
        is_staff=True,
        
    )

    Company.objects.create(

        user=user,

        company_name=data["company_name"],

        email=data["email"],

        phone=data["phone"],

        location=data["location"],

        description=data["description"],

        website=data.get(
            "website",
            ""
        ),

        verified=False,
    )

    return user
from django.db import transaction

from accounts.models import User
from students.models import University


@transaction.atomic
def register_university(data):
    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role="university",
        is_active=True,
         is_staff=True,
    )

    university = University.objects.create(
        user=user,
        name=data["university_name"],
        website=data.get("website", ""),
        logo=data.get("logo"),
        verified=False,
    )

    return user
