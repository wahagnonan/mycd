from django.urls import path

from .views import (
    ConversationListView,
    ConversationMessageListView,
    CreateConversationView,
    EncadreurDetailView,
    EncadreurListView,
    LoginView,
    MarkAsReadView,
    MatiereListView,
    MeView,
    MonProfilView,
    RegisterView,
    TokenRefreshView,
    api_root,
)

urlpatterns = [
    path("", api_root, name="api-root"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("encadreurs/", EncadreurListView.as_view(), name="encadreur-list"),
    path("encadreurs/<int:pk>/", EncadreurDetailView.as_view(), name="encadreur-detail"),
    path("mon-profil/", MonProfilView.as_view(), name="mon-profil"),
    path("matieres/", MatiereListView.as_view(), name="matiere-list"),
    # Messagerie
    path("messagerie/conversations/", ConversationListView.as_view(), name="conversation-list"),
    path("messagerie/conversations/create/", CreateConversationView.as_view(), name="conversation-create"),
    path("messagerie/conversations/<int:pk>/", ConversationMessageListView.as_view(), name="conversation-detail"),
    path("messagerie/conversations/<int:pk>/read/", MarkAsReadView.as_view(), name="conversation-read"),
]