from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from django.utils import timezone


class User(AbstractUser):

    ROLE_CHOICES = (
        ("student", "Student"),
        ("company", "Company"),
        ("admin", "Admin"),
        ("university", "University"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
    )
    class Meta:
        permissions = [
            (
                "view_university_dashboard",
                "Can view university dashboard",
            ),
            (
                "view_company_dashboard",
                "Can view company dashboard",
            ),
        ]
    def __str__(self):
        return self.username
    
from django.conf import settings
from django.db import models


class OTPCode(models.Model):

    PURPOSE_CHOICES = (
        ("login", "Login"),
        ("verify_email", "Verify Email"),
        ("verify_phone", "Verify Phone"),
        ("reset_password", "Reset Password"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_codes",
    )

    code = models.CharField(max_length=6)

    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    attempts = models.PositiveIntegerField(default=0)

    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.purpose}"
class LoginAttempt(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="login_attempts",
    )

    ip_address = models.GenericIPAddressField()

    successful = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

class LegalDocument(models.Model):

    DOCUMENT_TYPES = (
        ("terms", "Terms and Conditions"),
        ("privacy", "Privacy Policy"),
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
    )

    title = models.CharField(
        max_length=200
    )

    content = models.TextField()

    version = models.CharField(
        max_length=50
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} - v{self.version}"


class UserConsent(models.Model):
    """
    Records the user's acceptance of the specific
    Terms and Conditions and Privacy Policy versions.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consent",
    )

    terms_version = models.CharField(
        max_length=50
    )

    privacy_version = models.CharField(
        max_length=50
    )

    accepted_at = models.DateTimeField(
        default=timezone.now
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = "User Consent"
        verbose_name_plural = "User Consents"

    def __str__(self):
        return f"Consent for {self.user}"
    
    
    
    from django.db import models


class LandingPageSettings(models.Model):
    # =========================
    # HERO SECTION
    # =========================

    hero_badge = models.CharField(
        max_length=150,
        default="Your Internship Journey Starts Here"
    )

    hero_title = models.CharField(
        max_length=300,
        default="Connecting Students, Universities & Employers in One Platform"
    )

    hero_description = models.TextField(
        default=(
            "Discover internship opportunities, manage student placements, "
            "and connect universities with employers — all in one place."
        )
    )

    hero_image = models.ImageField(
        upload_to="landing/",
        blank=True,
        null=True
    )

    hero_primary_button = models.CharField(
        max_length=100,
        default="Find an Internship"
    )

    hero_secondary_button = models.CharField(
        max_length=100,
        default="Join Now"
    )

    # =========================
    # ABOUT SECTION
    # =========================

    about_badge = models.CharField(
        max_length=100,
        default="ABOUT US"
    )

    about_title = models.CharField(
        max_length=200,
        default="About InternConnect"
    )

    about_description = models.TextField(
        default=(
            "InternConnect is a digital platform that bridges the gap "
            "between students, universities and employers."
        )
    )

    about_image = models.ImageField(
        upload_to="landing/",
        blank=True,
        null=True
    )

    # =========================
    # MISSION / VISION / VALUES
    # =========================

    mission_title = models.CharField(
        max_length=100,
        default="Our Mission"
    )

    mission_text = models.TextField(
        default="Empower young talent through meaningful internships."
    )

    vision_title = models.CharField(
        max_length=100,
        default="Our Vision"
    )

    vision_text = models.TextField(
        default=(
            "A future where every student has access to quality "
            "internship opportunities."
        )
    )

    values_title = models.CharField(
        max_length=100,
        default="Our Values"
    )

    values_text = models.TextField(
        default="Integrity, Innovation, Collaboration, Impact."
    )

    # =========================
    # CTA SECTION
    # =========================

    cta_title = models.CharField(
        max_length=250,
        default="Ready to be part of the Internship Network?"
    )

    cta_description = models.TextField(
        default=(
            "Join thousands of students, universities and companies "
            "already on InternConnect."
        )
    )

    # =========================
    # FOOTER
    # =========================

    footer_description = models.TextField(
        blank=True,
        default="Connect students, universities and employers."
    )

    newsletter_title = models.CharField(
        max_length=150,
        default="Subscribe to Our Newsletter"
    )

    newsletter_description = models.TextField(
        default="Get the latest updates and opportunities."
    )

    copyright_text = models.CharField(
        max_length=250,
        default="© 2025 InternConnect. All rights reserved."
    )

    # =========================
    # SETTINGS
    # =========================

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Landing Page Settings"
        verbose_name_plural = "Landing Page Settings"

    def __str__(self):
        return "Landing Page Settings"
