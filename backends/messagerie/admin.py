from django.contrib import admin

from backends.messagerie.models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("parent", "encadreur", "updated_at", "created_at")
    list_filter = ("created_at",)
    search_fields = ("parent__email", "encadreur__email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__email", "content")
