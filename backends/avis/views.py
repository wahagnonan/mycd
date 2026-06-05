import logging

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from backends.accounts.permissions import IsParent
from backends.avis.models import Avis
from backends.avis.serializers import AvisSerializer
from backends.encadreurs.models import ProfilEncadreur

logger = logging.getLogger(__name__)


class AvisCreateView(generics.CreateAPIView):
    serializer_class = AvisSerializer
    permission_classes = (permissions.IsAuthenticated, IsParent)

    def perform_create(self, serializer):
        encadreur_id = self.kwargs["encadreur_pk"]
        encadreur = generics.get_object_or_404(ProfilEncadreur, id=encadreur_id)
        serializer.save(parent=self.request.user, encadreur=encadreur)
        logger.info(
            "AVIS_CREATED | Parent=%s (id=%d) | Encadreur=%s (id=%d) | Note=%d",
            self.request.user.email, self.request.user.id,
            encadreur.user.email, encadreur.id,
            serializer.validated_data["note"],
        )


class AvisByEncadreurView(generics.ListAPIView):
    serializer_class = AvisSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return Avis.objects.filter(
            encadreur_id=self.kwargs["encadreur_pk"]
        ).select_related("parent")


class AvisDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AvisSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Avis.objects.filter(parent=self.request.user)
