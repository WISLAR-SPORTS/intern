from .services import get_application_metrics


def university_metrics(request):

    if not request.user.is_authenticated:
        return {
            "application_metrics": None
        }

    if not request.path.startswith("/admin/"):
        return {
            "application_metrics": None
        }

    if request.user.is_superuser:
        university = None
    else:
        try:
            university = request.user.university
        except Exception:
            return {
                "application_metrics": None
            }

    return {
        "application_metrics": get_application_metrics(
            university=university
        )
    }
