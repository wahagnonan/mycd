import logging

from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from backends.accounts.models import User
from backends.encadreurs.models import ProfilEncadreur
from backends.messagerie.models import Conversation, Message
from backends.messagerie.serializers import (
    ConversationListSerializer,
    CreateConversationSerializer,
    MessageSerializer,
)
from backends.notifications.models import Notification
from backends.paiement.helpers import a_debloque_encadreur

logger = logging.getLogger(__name__)


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            models.Q(parent=user) | models.Q(encadreur=user)
        ).select_related("parent", "encadreur")


class CreateConversationView(generics.CreateAPIView):
    serializer_class = CreateConversationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        encadreur = User.objects.get(id=serializer.validated_data["encadreur_id"])

        if request.user.role == User.Role.PARENT:
            try:
                encadreur_profil = ProfilEncadreur.objects.get(user=encadreur)
            except ProfilEncadreur.DoesNotExist:
                return Response(
                    {"detail": "Encadreur introuvable"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not a_debloque_encadreur(request.user, encadreur_profil):
                return Response(
                    {
                        "detail": "Vous devez débloquer cet encadreur avant de le contacter. Achetez des crédits.",
                        "code": "credits_requis",
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

        conversation, created = Conversation.objects.get_or_create(
            parent=request.user,
            encadreur=encadreur,
        )
        if created:
            logger.info(
                "CONVERSATION_CREATED | Parent=%s (id=%d) | Encadreur=%s (id=%d)",
                request.user.email, request.user.id,
                encadreur.email, encadreur.id,
            )
        return Response({"id": conversation.id, "created": created})


class ConversationMessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        conv = Conversation.objects.get(id=self.kwargs["pk"])
        user = self.request.user
        if user not in (conv.parent, conv.encadreur):
            return Message.objects.none()
        return Message.objects.filter(conversation=conv).select_related("sender")

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(id=self.kwargs["pk"])
        user = self.request.user
        if user not in (conversation.parent, conversation.encadreur):
            raise PermissionDenied("Vous ne participez pas à cette conversation")
        msg = serializer.save(conversation=conversation, sender=user)
        destinataire = conversation.encadreur if user == conversation.parent else conversation.parent
        Notification.objects.create(
            user=destinataire,
            type=Notification.Type.NEW_MESSAGE,
            title=f"Nouveau message de {user.first_name or user.email}",
            message=msg.content[:100],
            link=f"/messagerie/{conversation.id}",
        )
        logger.info(
            "MESSAGE_SENT | Conversation=%d | Sender=%s (id=%d)",
            conversation.id, user.email, user.id,
        )


class MarkAsReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        conversation = Conversation.objects.get(id=pk)
        user = request.user
        if user not in (conversation.parent, conversation.encadreur):
            raise PermissionDenied("Vous ne participez pas à cette conversation")
        updated = conversation.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
        return Response({"marques_lus": updated})
