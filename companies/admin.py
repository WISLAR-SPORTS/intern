from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "email",
        "phone",
        "location",
        "verified",
        "latitude",
        "longitude",
    )

    list_filter = (
        "verified",
    )

    search_fields = (
        "company_name",
        "email",
        "phone",
        "location",
    )

    fields = (
        "user",
        "company_name",
        "email",
        "phone",
        "location",
        "description",
        "website",
        "verified",
        "logo",
        "latitude",
        "longitude",
    )

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        # Superuser sees everything
        if request.user.is_superuser:
            return queryset

        # Company users see only their own company
        if request.user.role == "company":
            return queryset.filter(
                user=request.user
            )

        # Other users see nothing
        return queryset

# admin.py
from django.contrib import admin
from django.urls import reverse
from django.shortcuts import redirect
from .models import LandingPageSettings


@admin.register(LandingPageSettings)
class LandingPageSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Branding", {
            "fields": ("site_name", "tagline", "logo", "logo_first", "logo_second"),
        }),
        ("Hero Section", {
            "fields": (
                "hero_badge", "hero_title", "hero_description", "hero_image",
                "hero_primary_button", "hero_primary_url",
                "hero_secondary_button", "hero_secondary_url",
            ),
        }),
        ("Features", {
            "fields": ("features_badge", "features_title", "features_description", "features"),
            "description": "features is a JSON list, e.g. "
                           '[{"icon": "📄", "title": "...", "description": "...", "color": "blue"}]',
        }),
        ("Network / Maps", {
            "fields": ("network_badge", "network_title", "network_description"),
        }),
        ("About Section", {
            "fields": (
                "about_badge", "about_title", "about_description", "about_image",
                "about_video_url", "about_video_text", "about_video_duration",
            ),
        }),
        ("Mission, Vision & Values", {
            "fields": (
                "mission_title", "mission_text",
                "vision_title", "vision_text",
                "values_title", "values_text",
            ),
        }),
        ("CTA Section", {
            "fields": (
                "cta_icon", "cta_title", "cta_description",
                "student_url", "university_url", "company_url",
            ),
        }),
        ("Footer", {
            "fields": (
                "footer_description",
                "newsletter_title", "newsletter_description", "newsletter_url",
                "copyright_text",
            ),
        }),
        ("Social Links", {
            "fields": ("facebook_url", "x_url", "linkedin_url", "youtube_url", "instagram_url"),
        }),
        ("Support Links", {
            "fields": ("help_url", "faq_url", "terms_url", "privacy_url"),
        }),
        ("Auth Links", {
            "fields": ("login_url", "get_started_url"),
        }),
    )

    readonly_fields = ()

    def has_add_permission(self, request):
        # Block creating a second row once one exists.
        return not LandingPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # This is a singleton — never allow deleting it.
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip the list page: go straight to the single instance,
        # creating it first if it doesn't exist yet.
        obj, _ = LandingPageSettings.objects.get_or_create(pk=1)
        return redirect(
            reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        )    