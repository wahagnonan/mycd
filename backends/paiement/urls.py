from django.urls import path

from backends.paiement.views import (
    CreditStatusView,
    DebloquerEncadreurView,
    HistoriquePaiementsView,
    InitierAchatCreditsView,
    InitierPaiementView,
    PaiementCallbackView,
    VerifierPaiementView,
)

urlpatterns = [
    path("paiement/initier/<int:encadreur_pk>/", InitierPaiementView.as_view(), name="paiement-initier"),
    path("paiement/callback/", PaiementCallbackView.as_view(), name="paiement-callback"),
    path("paiement/verifier/<str:token>/", VerifierPaiementView.as_view(), name="paiement-verifier"),
    path("paiement/historique/", HistoriquePaiementsView.as_view(), name="paiement-historique"),
    path("credits/statut/", CreditStatusView.as_view(), name="credit-statut"),
    path("credits/acheter/", InitierAchatCreditsView.as_view(), name="credit-acheter"),
    path("credits/debloquer/<int:encadreur_pk>/", DebloquerEncadreurView.as_view(), name="credit-debloquer"),
]
