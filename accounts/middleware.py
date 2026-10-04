from django.shortcuts import redirect
from django.urls import reverse

from .models import LegalDocument


class ConsentMiddleware:
    """
    Require authenticated users to accept the current
    Terms and Conditions and Privacy Policy before
    accessing protected pages.

    Superusers bypass the consent requirement.

    Anonymous users are ignored.

    The consent, terms, privacy, and logout pages remain
    accessible so users cannot become trapped in a
    redirect loop.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ==================================================
        # USER
        # ==================================================

        user = request.user

        # ==================================================
        # ANONYMOUS USERS
        # ==================================================

        if not user.is_authenticated:
            return self.get_response(request)

        # ==================================================
        # SUPERUSER BYPASS
        # ==================================================
        #
        # Django superusers do not need to accept the
        # normal user consent flow.
        #
        # This MUST happen before the consent check.
        #

        if user.is_superuser:
            return self.get_response(request)

        # ==================================================
        # STATIC / MEDIA
        # ==================================================

        if (
            request.path.startswith("/static/")
            or request.path.startswith("/media/")
        ):
            return self.get_response(request)

        # ==================================================
        # RESOLVE CURRENT URL SAFELY
        # ==================================================

        resolver_match = request.resolver_match

        current_url_name = (
            resolver_match.url_name
            if resolver_match is not None
            else None
        )

        # ==================================================
        # URLS THAT MUST ALWAYS BE ACCESSIBLE
        # ==================================================

        allowed_url_names = {
            "consent",
            "accept_consent",
            "terms",
            "privacy",
            "logout",
        }

        if current_url_name in allowed_url_names:
            return self.get_response(request)

        # ==================================================
        # CONSENT PAGE PATH FALLBACK
        # ==================================================
        #
        # This protects against resolver_match being None.
        #

        consent_url = reverse("consent")

        if request.path == consent_url:
            return self.get_response(request)

        # ==================================================
        # GET CURRENT TERMS
        # ==================================================

        terms_document = (
            LegalDocument.objects
            .filter(
                document_type="terms",
                is_active=True,
            )
            .order_by("-updated_at")
            .first()
        )

        # ==================================================
        # GET CURRENT PRIVACY POLICY
        # ==================================================

        privacy_document = (
            LegalDocument.objects
            .filter(
                document_type="privacy",
                is_active=True,
            )
            .order_by("-updated_at")
            .first()
        )

        # ==================================================
        # LEGAL DOCUMENTS NOT CONFIGURED
        # ==================================================
        #
        # Do not allow normal users into protected pages
        # if the current legal documents are missing.
        #

        if not terms_document or not privacy_document:

            return redirect(
                consent_url
            )

        # ==================================================
        # GET USER CONSENT
        # ==================================================

        consent = getattr(
            user,
            "consent",
            None,
        )

        # ==================================================
        # CHECK CURRENT CONSENT
        # ==================================================
        #
        # The user must have accepted BOTH current versions.
        #

        has_current_consent = (
            consent is not None
            and consent.terms_version
            == terms_document.version
            and consent.privacy_version
            == privacy_document.version
        )

        # ==================================================
        # USER HAS CURRENT CONSENT
        # ==================================================

        if has_current_consent:
            return self.get_response(request)

        # ==================================================
        # USER NEEDS TO ACCEPT / RE-ACCEPT
        # ==================================================

        # Only pass the local path to the consent page.
        #
        # request.get_full_path() includes query parameters,
        # while request.path only contains the local path.

        next_url = request.path

        return redirect(
            f"{consent_url}?next={next_url}"
        )
