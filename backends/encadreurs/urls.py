from django.urls import path

from backends.encadreurs.views import (
    EncadreurDetailView,
    EncadreurListView,
    MatiereListView,
    MonProfilView,
)

urlpatterns = [
    path("encadreurs/", EncadreurListView.as_view(), name="encadreur-list"),
    path("encadreurs/<int:pk>/", EncadreurDetailView.as_view(), name="encadreur-detail"),
    path("mon-profil/", MonProfilView.as_view(), name="mon-profil"),
    path("matieres/", MatiereListView.as_view(), name="matiere-list"),
]
