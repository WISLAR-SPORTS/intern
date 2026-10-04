from .models import LandingPageSettings


def landing_settings(request):
    settings = LandingPageSettings.objects.first()

    return {
        "settings": settings,
    }
