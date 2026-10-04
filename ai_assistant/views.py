import json
import traceback

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .agent import run_agent

@login_required
@require_POST
def chat(request):

    # ============================================
    # CHECK USER ROLE
    # ============================================

    if request.user.role != "student":

        return JsonResponse(
            {
                "error": (
                    "The AI assistant is available "
                    "to students only."
                )
            },
            status=403,
        )


    # ============================================
    # READ REQUEST DATA
    # ============================================

    try:

        data = json.loads(
            request.body
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid request."
            },
            status=400,
        )


    # ============================================
    # GET STUDENT MESSAGE
    # ============================================

    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return JsonResponse(
            {
                "error": "Message cannot be empty."
            },
            status=400,
        )


    # ============================================
    # RUN AI AGENT
    # ============================================

    try:

        response = run_agent(
            user=request.user,
            message=message,
        )


    except Exception as e:

        print(
            "============================================"
        )

        print(
            "AI ASSISTANT ERROR"
        )

        print(
            "============================================"
        )

        print(
            "Error:",
            e
        )

        print(
            "Type:",
            type(e).__name__
        )

        traceback.print_exc()

        print(
            "============================================"
        )


        return JsonResponse(
            {
                "error": (
                    "The AI assistant is "
                    "temporarily unavailable."
                )
            },
            status=500,
        )


    # ============================================
    # PREPARE RESPONSE
    # ============================================

    if isinstance(response, dict):

        ai_message = response.get(
            "message",
            ""
        )

        learning_url = response.get(
            "learning_url"
        )

    else:

        ai_message = response

        learning_url = None


    # ============================================
    # RETURN AI RESPONSE
    # ============================================

    return JsonResponse(
        {
            "message": ai_message,

            "learning_url": learning_url,
        }
    )
