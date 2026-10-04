from django.contrib import admin

from .models import (
    Conversation,
    Message,
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-updated_at",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "role",
        "created_at",
    )

    list_filter = (
        "role",
        "created_at",
    )

    search_fields = (
        "content",
        "conversation__user__username",
        "conversation__user__email",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )
