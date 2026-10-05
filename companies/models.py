from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
class Company(models.Model):

    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="company",
)


    company_name = models.CharField(
        max_length=200
    )


    email = models.EmailField()


    phone = models.CharField(
        max_length=20
    )


    location = models.CharField(
        max_length=200
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )


    description = models.TextField()


    website = models.URLField(
        blank=True
    )


    verified = models.BooleanField(
        default=False
    )


    logo = models.ImageField(
        upload_to="companies/",
        blank=True,
        null=True
    )
  


    def __str__(self):

        return self.company_name
    

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

    hero_image = CloudinaryField(
    "hero_image",
    folder="landing/",
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
    about_image = CloudinaryField(
        "about_image",
        folder="landing/",
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
    site_name = models.CharField(max_length=100, default="InternConnect")
    tagline = models.CharField(max_length=200, default="Connect. Intern. Grow.")
    logo = CloudinaryField(
    "logo",
    folder="landing/",
    blank=True,
    null=True
)
    logo_first = models.CharField(max_length=50, default="Intern")
    logo_second = models.CharField(max_length=50, default="Connect")
        
    features_badge = models.CharField(max_length=100, default="OUR FEATURES")
    features_title = models.CharField(max_length=250, default="Everything You Need for a Successful Internship")
    features_description = models.TextField(default="Powerful features designed for students, universities and companies.")
    features = models.JSONField(default=list, blank=True)
        
    network_badge = models.CharField(max_length=100, default="EXPLORE OUR NETWORK")
    network_title = models.CharField(max_length=250, default="Universities & Companies Across Uganda")
    network_description = models.TextField(default="Explore the locations of universities and companies participating in our platform.")
        
    cta_icon = models.CharField(max_length=20, default="🎓")
    student_url = models.CharField(max_length=250, blank=True)
    university_url = models.CharField(max_length=250, blank=True)
    company_url = models.CharField(max_length=250, blank=True)
        
    login_url = models.CharField(max_length=250, blank=True)
    get_started_url = models.CharField(max_length=250, blank=True)
        
    hero_primary_url = models.CharField(max_length=250, blank=True)
    hero_secondary_url = models.CharField(max_length=250, blank=True)
        
    about_video_url = models.URLField(blank=True)
    about_video_text = models.CharField(max_length=100, default="Watch Our Story")
    about_video_duration = models.CharField(max_length=20, default="2:30")
        
    facebook_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
        
    help_url = models.CharField(max_length=250, blank=True)
    faq_url = models.CharField(max_length=250, blank=True)
    terms_url = models.CharField(max_length=250, blank=True)
    privacy_url = models.CharField(max_length=250, blank=True)
    newsletter_url = models.CharField(max_length=250, blank=True)
    
    

    # =========================
    # SETTINGS
    # =========================

updated_at = models.DateTimeField(auto_now=True)

class Meta:
        verbose_name = "Landing Page Settings"
        verbose_name_plural = "Landing Page Settings"

def __str__(self):
        return "Landing Page Settings"
