from django.urls import path

from .views import chat, ai_assistant


urlpatterns = [
    path(
        "chat/",
        chat,
        name="ai_chat",
    ),
    path(
            "ai-assistant/",
            ai_assistant,
            name="ai_assistant",
        ),
  

    path(
        "ai-assistant/chat/",
        chat,
        name="ai_chat",
    ),
]
