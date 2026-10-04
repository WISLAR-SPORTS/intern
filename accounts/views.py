
import httpx
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from companies.models import Company
from students.models import University
from django.utils import timezone
import secrets
from .models import OTPCode
from django.core.mail import send_mail
from brevo.core.api_error import ApiError
from .utils import verify_turnstile
from django.conf import settings
from companies.models import LandingPageSettings




from .forms import (
    LoginForm,
    StudentRegistrationForm,
    CompanyRegistrationForm,
    UniversityRegistrationForm,
    PasswordLoginForm,
    OTPVerificationForm,
)

from .service import (
    authenticate_user,
    get_login_redirect,
    register_student,
    register_company,
    register_university,
    get_user_by_email,
    authenticate_user,
    validate_user_account,
  
    
   
)

def web_login(request):

    if request.user.is_authenticated:
        return redirect(
            get_login_redirect(request.user)
        )

    form = LoginForm(
        request.POST or None
    )

    if request.method == "POST":

        # ============================================
        # VERIFY HUMAN
        # ============================================

        if not verify_turnstile(request):

            form.add_error(
                None,
                "Please complete the human verification."
            )

        elif form.is_valid():

            email = form.cleaned_data["email"]

            user = get_user_by_email(email)

            if user is None:

                form.add_error(
                    "email",
                    "No account exists with this email."
                )

            else:

                error = validate_user_account(user)

                if error:

                    form.add_error(
                        None,
                        error
                    )

                else:

                    request.session["login_email"] = (
                        user.email
                    )

                    return redirect(
                        "login_method"
                    )
    site_settings = LandingPageSettings.objects.first()
    return render(
        request,
        "login.html",
        {
            "form": form,
            "turnstile_site_key":
                settings.TURNSTILE_SITE_KEY,
                "site_settings": site_settings,
        },
    )

def login_method(request):

    if request.user.is_authenticated:
        return redirect(
            get_login_redirect(request.user)
        )

    email = request.session.get(
        "login_email"
    )

    if not email:
        return redirect("login")

    user = get_user_by_email(email)

    if user is None:
        request.session.pop(
            "login_email",
            None
        )

        return redirect("login")
    site_settings = LandingPageSettings.objects.first()

    return render(
        request,
        "login_method.html",
        {
            "email": email,
            "site_settings": site_settings,
        },
    )
def password_login(request):

    if request.user.is_authenticated:
        return redirect(
            get_login_redirect(request.user)
        )

    email = request.session.get(
        "login_email"
    )

    if not email:
        return redirect("login")

    form = PasswordLoginForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            password = form.cleaned_data["password"]

            user = authenticate_user(
                email=email,
                password=password,
            )

            if user is None:

                form.add_error(
                    None,
                    "Invalid password."
                )

            else:

                error = validate_user_account(user)

                if error:
                    form.add_error(
                        None,
                        error
                    )

                else:

                    # Clear temporary login session
                    request.session.pop(
                        "login_email",
                        None
                    )

                    login(
                        request,
                        user
                    )

                    return redirect(
                        get_login_redirect(user)
                    )
    site_settings = LandingPageSettings.objects.first()
    return render(
        request,
        "password_login.html",
        {
            "form": form,
            "email": email,
            "site_settings": site_settings,
        },
    )


from .email_service import send_otp_email

def request_otp(request):

    # =================================================
    # ALREADY AUTHENTICATED
    # =================================================

    if request.user.is_authenticated:
        return redirect(
            get_login_redirect(request.user)
        )

    # =================================================
    # GET LOGIN EMAIL FROM SESSION
    # =================================================

    email = request.session.get("login_email")

    if not email:
        return redirect("login")

    # =================================================
    # FIND USER
    # =================================================

    user = get_user_by_email(email)

    if user is None:
        messages.error(
            request,
            "We couldn't find an account with that email.",
        )

        return redirect("login")

    # =================================================
    # VALIDATE ACCOUNT
    # =================================================

    error = validate_user_account(user)

    if error:
        messages.error(
            request,
            error,
        )

        return redirect("login")

    # =================================================
    # INVALIDATE PREVIOUS OTPs
    # =================================================

    OTPCode.objects.filter(
        user=user,
        purpose="login",
        used=False,
    ).update(
        used=True
    )

    # =================================================
    # GENERATE OTP
    # =================================================

    otp = f"{secrets.randbelow(1_000_000):06d}"

    expires_at = (
        timezone.now()
        + timezone.timedelta(minutes=5)
    )

    # =================================================
    # CREATE OTP
    # =================================================

    otp_record = OTPCode.objects.create(
        user=user,
        code=otp,
        purpose="login",
        expires_at=expires_at,
    )

    # =================================================
    # SEND OTP
    # =================================================

    try:

        send_otp_email(
            email=user.email,
            otp=otp,
            expiry_minutes=5,
        )

    # -------------------------------------------------
    # TIMEOUT
    # -------------------------------------------------

    except httpx.TimeoutException:

        print("OTP EMAIL ERROR: TIMEOUT")

        otp_record.delete()

        messages.error(
            request,
            "The email service took too long to respond. "
            "Please try again.",
        )

        return redirect(
            "login_method"
        )

    # -------------------------------------------------
    # CONNECTION / NETWORK ERROR
    # -------------------------------------------------

    except (
        httpx.ConnectError,
        httpx.NetworkError,
    ):

        print("OTP EMAIL ERROR: NETWORK")

        otp_record.delete()

        messages.error(
            request,
            "We couldn't connect to the email service. "
            "Please try again.",
        )

        return redirect(
            "login_method"
        )

    # -------------------------------------------------
    # BREVO API ERROR
    # -------------------------------------------------

    except ApiError as e:

        print("================================")
        print("BREVO OTP ERROR")
        print("Status:", e.status_code)
        print("Body:", e.body)
        print("================================")

        otp_record.delete()

        messages.error(
            request,
            "We couldn't send your verification code. "
            "Please try again.",
        )

        return redirect(
            "login_method"
        )

    # -------------------------------------------------
    # UNEXPECTED ERROR
    # -------------------------------------------------

    except Exception as e:

        print("================================")
        print("UNEXPECTED OTP EMAIL ERROR")
        print(type(e).__name__)
        print(str(e))
        print("================================")

        otp_record.delete()

        messages.error(
            request,
            "Something went wrong while sending your "
            "verification code. Please try again.",
        )

        return redirect(
            "login_method"
        )

    # =================================================
    # EMAIL SENT SUCCESSFULLY
    # =================================================

    return redirect(
        "verify_otp"
    )



def verify_otp(request):

    if request.user.is_authenticated:
        return redirect(
            get_login_redirect(request.user)
        )

    email = request.session.get(
        "login_email"
    )

    if not email:
        return redirect("login")

    user = get_user_by_email(email)

    if user is None:
        return redirect("login")

    form = OTPVerificationForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            otp = form.cleaned_data["otp"]

            otp_code = (
                OTPCode.objects
                .filter(
                    user=user,
                    purpose="login",
                    used=False,
                )
                .order_by("-created_at")
                .first()
            )

            if otp_code is None:

                form.add_error(
                    "otp",
                    "Invalid or expired OTP."
                )

            elif otp_code.expires_at < timezone.now():

                otp_code.used = True
                otp_code.save(
                    update_fields=["used"]
                )

                form.add_error(
                    "otp",
                    "This OTP has expired."
                )

            elif otp_code.attempts >= 5:

                otp_code.used = True
                otp_code.save(
                    update_fields=["used"]
                )

                form.add_error(
                    "otp",
                    "Too many attempts. Please request a new code."
                )

            elif otp_code.code != otp:

                otp_code.attempts += 1

                otp_code.save(
                    update_fields=["attempts"]
                )

                form.add_error(
                    "otp",
                    "Invalid OTP."
                )

            else:

                # OTP is valid
                otp_code.used = True

                otp_code.save(
                    update_fields=["used"]
                )

                error = validate_user_account(user)

                if error:

                    form.add_error(
                        None,
                        error
                    )

                else:

                    request.session.pop(
                        "login_email",
                        None
                    )

                    login(
                        request,
                        user
                    )

                    return redirect(
                        get_login_redirect(user)
                    )
    site_settings = LandingPageSettings.objects.first()
    return render(
        request,
        "otp_verify.html",
        {
            "form": form,
            "email": email,
            "site_settings": site_settings,
        },
    )



def web_logout(request):

    logout(request)

    return redirect("login")


def register(request):

    student_form = StudentRegistrationForm()
    company_form = CompanyRegistrationForm()
    university_form = UniversityRegistrationForm()


    if request.method == "POST":

        registration_type = request.POST.get(
            "registration_type"
        )

        # ==========================================
        # STUDENT
        # ==========================================

        if registration_type == "student":

            student_form = StudentRegistrationForm(
                request.POST
            )

            if student_form.is_valid():

                try:
                    register_student(
                        student_form.cleaned_data
                    )

                    messages.success(
                        request,
                        "Student account created successfully. "
                        "You can now log in."
                    )

                    return redirect("login")

                except ValueError as error:
                    student_form.add_error(
                        "registration_number",
                        str(error),
                    )


        # ==========================================
        # COMPANY
        # ==========================================

        elif registration_type == "company":

            company_form = CompanyRegistrationForm(
                request.POST
            )

            if company_form.is_valid():

                register_company(
                    company_form.cleaned_data
                )

                messages.success(
                    request,
                    "Company registration submitted successfully. "
                    "Please wait for administrator verification."
                )

                return redirect("login")
            
            
            """university registration """
        elif registration_type == "university":
                university_form = UniversityRegistrationForm(
                     request.POST,
                     request.FILES,
    )

                if university_form.is_valid():
                 register_university(
                    university_form.cleaned_data
                )

                messages.success(
                    request,
                    "University registration submitted successfully. "
                    "Your account is pending administrator verification.",
                )

                return redirect("login")

    site_settings = LandingPageSettings.objects.first()
    return render(
        request,
        "register.html",
       
        {
            "student_form": student_form,
            "company_form": company_form,
             "university_form": university_form,
             "site_settings": site_settings,
        }
    )
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from .models import  UserConsent


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST

from django.contrib.auth.decorators import login_required

from django.utils import timezone
from .models import UserConsent, LegalDocument


# ============================================================
# GET CURRENT TERMS
# ============================================================

def get_current_terms():
    return LegalDocument.objects.filter(
        document_type="terms",
        is_active=True,
    ).first()


# ============================================================
# GET CURRENT PRIVACY POLICY
# ============================================================

def get_current_privacy():
    return LegalDocument.objects.filter(
        document_type="privacy",
        is_active=True,
    ).first()


# ============================================================
# CONSENT PAGE
# ============================================================

@login_required
@require_GET
def consent_view(request):

    terms_document = get_current_terms()
    privacy_document = get_current_privacy()

    if not terms_document or not privacy_document:
        return render(
            request,
            "consent_error.html",
            {
                "message": (
                    "The Terms and Conditions or Privacy Policy "
                    "has not been configured yet."
                )
            },
            status=503,
        )

    consent = getattr(
        request.user,
        "consent",
        None,
    )

    # User already accepted the current versions
    if (
        consent
        and consent.terms_version == terms_document.version
        and consent.privacy_version == privacy_document.version
    ):
        return redirect("student_dashboard")

    next_url = request.GET.get(
        "next",
        "",
    )

    return render(
        request,
        "consent.html",
        {
            "next_url": next_url,
            "terms_document": terms_document,
            "privacy_document": privacy_document,
        },
    )


# ============================================================
# ACCEPT CONSENT
# ============================================================

@login_required
@require_POST
def accept_consent(request):

    accepted = request.POST.get("accepted")

    if accepted != "true":
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "You must accept the Terms and Conditions "
                    "and Privacy Policy."
                ),
            },
            status=400,
        )

    terms_document = get_current_terms()
    privacy_document = get_current_privacy()

    if not terms_document or not privacy_document:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "The current legal documents are "
                    "not available."
                ),
            },
            status=503,
        )

    ip_address = request.META.get(
        "REMOTE_ADDR"
    )

    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        "",
    )

    UserConsent.objects.update_or_create(
        user=request.user,
        defaults={
            "terms_version": terms_document.version,
            "privacy_version": privacy_document.version,
            "accepted_at": timezone.now(),
            "ip_address": ip_address,
            "user_agent": user_agent,
        },
    )

    next_url = request.POST.get(
        "next",
        "",
    )

    # Prevent open redirects
    if (
        not next_url
        or not next_url.startswith("/")
        or next_url.startswith("//")
    ):
        next_url = "/studentdashboard/"

    return JsonResponse(
        {
            "success": True,
            "redirect_url": next_url,
        }
    )


# ============================================================
# TERMS
# ============================================================

@require_GET
def terms(request):

    document = get_current_terms()

    if not document:
        return render(
            request,
            "legal_error.html",
            {
                "message": (
                    "The Terms and Conditions are "
                    "currently unavailable."
                )
            },
            status=503,
        )

    return render(
        request,
        "terms.html",
        {
            "document": document,
        },
    )


# ============================================================
# PRIVACY
# ============================================================

@require_GET
def privacy(request):

    document = get_current_privacy()

    if not document:
        return render(
            request,
            "legal_error.html",
            {
                "message": (
                    "The Privacy Policy is "
                    "currently unavailable."
                )
            },
            status=503,
        )

    return render(
        request,
        "aprivacy.html",
        {
            "document": document,
        },
    )
