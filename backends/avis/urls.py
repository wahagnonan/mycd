from django.urls import path

from backends.avis.views import (
    AvisByEncadreurView,
    AvisCreateView,
    AvisDetailView,
)

urlpatterns = [
    path("encadreurs/<int:encadreur_pk>/avis/", AvisCreateView.as_view(), name="avis-create"),
    path("encadreurs/<int:encadreur_pk>/avis/liste/", AvisByEncadreurView.as_view(), name="avis-list"),
    path("encadreurs/<int:encadreur_pk>/avis/<int:pk>/", AvisDetailView.as_view(), name="avis-detail"),
]
