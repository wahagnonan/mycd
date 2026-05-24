from django.urls import path

from .views import (
    AvisByEncadreurView,
    AvisCreateView,
    AvisDetailView,
    ConversationListView,
    ConversationMessageListView,
    CreateConversationView,
    EncadreurDetailView,
    EncadreurListView,
    HistoriquePaiementsView,
    InitierPaiementView,
    LoginView,
    MarkAllNotificationsReadView,
    MarkAsReadView,
    MarkNotificationReadView,
    MatiereListView,
    MeView,
    MonProfilView,
    NotificationListView,
    PaiementCallbackView,
    RegisterView,
    TokenRefreshView,
    VerifierAccesView,
    VerifierPaiementView,
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
    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
    path("notifications/read-all/", MarkAllNotificationsReadView.as_view(), name="notification-read-all"),
    # Avis
    path("encadreurs/<int:encadreur_pk>/avis/", AvisCreateView.as_view(), name="avis-create"),
    path("encadreurs/<int:encadreur_pk>/avis/liste/", AvisByEncadreurView.as_view(), name="avis-list"),
    path("encadreurs/<int:encadreur_pk>/avis/<int:pk>/", AvisDetailView.as_view(), name="avis-detail"),
    # Paiement
    path("paiement/initier/<int:encadreur_pk>/", InitierPaiementView.as_view(), name="paiement-initier"),
    path("paiement/callback/", PaiementCallbackView.as_view(), name="paiement-callback"),
    path("paiement/verifier/<str:token>/", VerifierPaiementView.as_view(), name="paiement-verifier"),
    path("paiement/historique/", HistoriquePaiementsView.as_view(), name="paiement-historique"),
    # Accès
    path("encadreurs/<int:encadreur_pk>/verifier-acces/", VerifierAccesView.as_view(), name="verifier-acces"),
]