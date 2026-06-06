import logging

from django.db import models
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import UserRateThrottle

from backends.accounts.models import User
from backends.accounts.permissions import IsEncadreur
from backends.encadreurs.models import Matiere, ProfilEncadreur
from backends.encadreurs.serializers import MatiereSerializer, ProfilEncadreurSerializer

logger = logging.getLogger(__name__)


class MonProfilThrottle(UserRateThrottle):
    scope = "mon-profil"


class MonProfilPatchThrottle(UserRateThrottle):
    scope = "mon-profil-patch"


class EncadreurListView(generics.ListAPIView):
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        qs = ProfilEncadreur.objects.filter(disponible=True).select_related("user")

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                models.Q(user__first_name__icontains=search)
                | models.Q(user__last_name__icontains=search)
                | models.Q(bio__icontains=search)
            )

        ville = self.request.query_params.get("ville")
        if ville:
            qs = qs.filter(user__ville__icontains=ville)
        quartier = self.request.query_params.get("quartier")
        if quartier:
            qs = qs.filter(user__quartier__icontains=quartier)

        matiere = self.request.query_params.get("matiere")
        if matiere:
            qs = qs.filter(matieres__id=matiere)
        matiere_nom = self.request.query_params.get("matiere_nom")
        if matiere_nom:
            qs = qs.filter(autre_matiere__icontains=matiere_nom)

        note_min = self.request.query_params.get("note_min")
        if note_min:
            try:
                qs = qs.filter(note_moyenne__gte=float(note_min))
            except ValueError:
                pass

        niveau_etudes = self.request.query_params.get("niveau_etudes")
        if niveau_etudes:
            qs = qs.filter(niveau_etudes=niveau_etudes)

        niveaux_ens = self.request.query_params.getlist("niveaux_enseignement")
        for niv in niveaux_ens:
            qs = qs.filter(niveaux_enseignement__contains=niv)

        jours = self.request.query_params.getlist("jours_disponibles")
        for jour in jours:
            qs = qs.filter(jours_disponibles__contains=jour)

        tarif_max_mois = self.request.query_params.get("tarif_max_mois")
        if tarif_max_mois:
            try:
                qs = qs.filter(
                    models.Q(tarif_mois__lte=int(tarif_max_mois))
                    | models.Q(tarif_mois__isnull=True)
                )
            except ValueError:
                pass

        tarif_max_horaire = self.request.query_params.get("tarif_max_horaire")
        if tarif_max_horaire:
            try:
                qs = qs.filter(
                    models.Q(tarif_horaire__lte=int(tarif_max_horaire))
                    | models.Q(tarif_horaire__isnull=True)
                )
            except ValueError:
                pass

        ordering = self.request.query_params.get("ordering")
        if ordering in ("note", "-note", "tarif_mois", "-tarif_mois",
                         "tarif_horaire", "-tarif_horaire",
                         "date_inscription", "-date_inscription"):
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-date_inscription")

        return qs


class EncadreurDetailView(generics.RetrieveAPIView):
    queryset = ProfilEncadreur.objects.select_related("user")
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.AllowAny,)


class MonProfilView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.IsAuthenticated, IsEncadreur)

    def get_throttles(self):
        if self.request.method == "PATCH":
            return [MonProfilPatchThrottle()]
        return [MonProfilThrottle()]

    def get_object(self):
        if self.request.user.role != User.Role.ENCADREUR:
            raise PermissionDenied("Seuls les encadreurs peuvent accéder à leur profil")
        profil, created = ProfilEncadreur.objects.get_or_create(user=self.request.user)
        if created:
            logger.info(
                "PROFIL_CREATED | User=%s (id=%d)",
                self.request.user.email, self.request.user.id,
            )
        return profil

    def perform_update(self, serializer):
        logger.info(
            "PROFIL_UPDATED | User=%s (id=%d)",
            self.request.user.email, self.request.user.id,
        )
        return super().perform_update(serializer)


class MatiereListView(generics.ListAPIView):
    queryset = Matiere.objects.all().order_by("nom")
    serializer_class = MatiereSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
