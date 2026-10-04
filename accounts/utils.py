import requests

from django.conf import settings


def verify_turnstile(request):

    token = request.POST.get(
        "cf-turnstile-response"
    )

    if not token:
        return False

    try:

        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",

            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": request.META.get(
                    "REMOTE_ADDR"
                ),
            },

            timeout=10,
        )

        result = response.json()

        return result.get(
            "success",
            False
        )

    except requests.RequestException:

        return False
