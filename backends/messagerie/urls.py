from django.urls import path

from backends.messagerie.views import (
    ConversationListView,
    ConversationMessageListView,
    CreateConversationView,
    MarkAsReadView,
)

urlpatterns = [
    path("messagerie/conversations/", ConversationListView.as_view(), name="conversation-list"),
    path("messagerie/conversations/create/", CreateConversationView.as_view(), name="conversation-create"),
    path("messagerie/conversations/<int:pk>/", ConversationMessageListView.as_view(), name="conversation-detail"),
    path("messagerie/conversations/<int:pk>/read/", MarkAsReadView.as_view(), name="conversation-read"),
]
