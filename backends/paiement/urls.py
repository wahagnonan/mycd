from django.urls import path

from backends.paiement.views import (
    CreditStatusView,
    DebloquerEncadreurView,
    InitierAchatCreditsView,
    PaiementCallbackView,
)

urlpatterns = [
    path("paiement/callback/", PaiementCallbackView.as_view(), name="paiement-callback"),
    path("credits/statut/", CreditStatusView.as_view(), name="credit-statut"),
    path("credits/acheter/", InitierAchatCreditsView.as_view(), name="credit-acheter"),
    path("credits/debloquer/<int:encadreur_pk>/", DebloquerEncadreurView.as_view(), name="credit-debloquer"),
]
