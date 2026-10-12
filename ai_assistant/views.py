import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .agent import run_agent

logger = logging.getLogger(__name__)


@login_required
@require_POST
def chat(request):
    # Check student role
    if getattr(request.user, "role", None) != "student":
        return JsonResponse(
            {"error": "The AI assistant is available to students only."},
            status=403,
        )

    # Parse request
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid request."},
            status=400,
        )

    # Validate message
    message = data.get("message", "")

    if not isinstance(message, str):
        return JsonResponse(
            {"error": "Message must be text."},
            status=400,
        )

    message = message.strip()

    if not message:
        return JsonResponse(
            {"error": "Message cannot be empty."},
            status=400,
        )

    if len(message) > 2000:
        return JsonResponse(
            {"error": "Message is too long."},
            status=400,
        )

    # Run your existing AI agent
    try:
        response = run_agent(
            user=request.user,
            message=message,
        )
    except Exception:
        logger.exception("AI assistant error")
        return JsonResponse(
            {"error": "The AI assistant is temporarily unavailable."},
            status=500,
        )

    # Normalize the response
    if isinstance(response, dict):
        ai_message = response.get("message", "")
        learning_url = response.get("learning_url")
    else:
        ai_message = response
        learning_url = None

    if not isinstance(ai_message, str):
        ai_message = str(ai_message) if ai_message is not None else ""

    return JsonResponse({
        "message": ai_message,
        "learning_url": learning_url,
    })


@login_required
def ai_assistant(request):
    if getattr(request.user, "role", None) != "student":
        from django.shortcuts import redirect
        return redirect("dashboard")

    return render(
        request,
        "dashboard/ai-assistant.html",
    )