import hmac
import hashlib
import json
import logging

from django.conf import settings
from django.db import models, transaction
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backends.accounts.models import User
from backends.accounts.permissions import IsParent
from backends.encadreurs.models import ProfilEncadreur
from backends.messagerie.models import Conversation
from backends.notifications.models import Notification
from backends.paiement.helpers import a_debloque_encadreur, get_credits_restants
from backends.paiement.models import CreditAchat, CreditUtilisation, Paiement
from backends.paiement.serializers import (
    CreditAchatSerializer,
    InitierPaiementSerializer,
    PaiementSerializer,
)

logger = logging.getLogger(__name__)


class InitierPaiementView(generics.GenericAPIView):
    serializer_class = InitierPaiementSerializer
    permission_classes = (permissions.IsAuthenticated, IsParent)

    def post(self, request, encadreur_pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        encadreur = generics.get_object_or_404(ProfilEncadreur, id=encadreur_pk)

        from backends.paiement.paydunya import creer_facture

        parent_nom = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
        description = serializer.validated_data.get("description") or f"Paiement pour {encadreur.user.email}"

        paiement = Paiement.objects.create(
            parent=request.user,
            encadreur=encadreur,
            montant=serializer.validated_data["montant"],
            type=serializer.validated_data["type"],
            description=description,
        )

        try:
            succes, response = creer_facture(
                montant=paiement.montant,
                description=description,
                parent_nom=parent_nom,
                parent_email=request.user.email,
                parent_phone=request.user.phone,
                paiement_id=paiement.id,
            )

            if succes:
                paiement.token_paydunya = response.get("token", "")
                paiement.receipt_url = response.get("receipt_url", "")
                paiement.save(update_fields=["token_paydunya", "receipt_url"])
                logger.info(
                    "PAIEMENT_INITIE | id=%d | montant=%d | token=%s",
                    paiement.id, paiement.montant, paiement.token_paydunya,
                )
                return Response({
                    "paiement_id": paiement.id,
                    "invoice_url": response.get("response_text"),
                    "token": paiement.token_paydunya,
                })
            else:
                paiement.statut = Paiement.Statut.ECHOUE
                paiement.save(update_fields=["statut"])
                logger.warning(
                    "PAIEMENT_ECHEC | id=%d | response=%s",
                    paiement.id, response,
                )
                return Response(
                    {"detail": "Erreur lors de la création de la facture PayDunya"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
        except Exception:
            paiement.statut = Paiement.Statut.ECHOUE
            paiement.save(update_fields=["statut"])
            logger.exception("PAIEMENT_EXCEPTION | id=%d", paiement.id)
            return Response(
                {"detail": "Erreur lors de la communication avec PayDunya"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


@method_decorator(csrf_exempt, name="dispatch")
class PaiementCallbackView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, TypeError, AttributeError):
            return Response({"detail": "Données JSON invalides"}, status=status.HTTP_400_BAD_REQUEST)

        received_hash = body.pop("hash", "")
        raw_data = json.dumps(body, separators=(",", ":"))

        master_key = settings.PAYDUNYA["MASTER_KEY"]
        expected_hash = hmac.new(
            master_key.encode(), raw_data.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_hash, expected_hash):
            logger.warning("PAIEMENT_CALLBACK_HASH_INVALIDE | hash=%s", received_hash)
            return Response({"detail": "Hash invalide"}, status=status.HTTP_403_FORBIDDEN)

        status_pay = body.get("status")
        token = body.get("invoice", {}).get("token", "")
        receipt_url = body.get("receipt_url", "")

        if status_pay == "completed":
            with transaction.atomic():
                updated = Paiement.objects.filter(
                    token_paydunya=token, statut=Paiement.Statut.EN_ATTENTE
                ).update(
                    statut=Paiement.Statut.COMPLETE,
                    receipt_url=receipt_url,
                )
                if updated:
                    paiement = Paiement.objects.get(token_paydunya=token)
                    Notification.objects.create(
                        user=paiement.encadreur.user,
                        type=Notification.Type.PAYMENT_RECEIVED,
                        title=f"Paiement reçu de {paiement.parent.email}",
                        message=f"{paiement.montant} FCFA — {paiement.description[:100]}",
                        link="/messagerie",
                    )
                    logger.info(
                        "PAIEMENT_COMPLETE | token=%s | montant=%d",
                        token, paiement.montant,
                    )
                else:
                    updated = CreditAchat.objects.filter(
                        token_paydunya=token, statut=CreditAchat.Statut.EN_ATTENTE
                    ).update(
                        statut=CreditAchat.Statut.COMPLETE,
                        receipt_url=receipt_url,
                    )
                    if updated:
                        credit_achat = CreditAchat.objects.get(token_paydunya=token)
                        Notification.objects.create(
                            user=credit_achat.parent,
                            type=Notification.Type.PAYMENT_RECEIVED,
                            title="Achat de crédits réussi",
                            message=f"Vous avez acheté {credit_achat.credits_achetes} crédits de contact.",
                            link="/encadreurs",
                        )
                        logger.info(
                            "CREDIT_ACHAT_COMPLETE | id=%d | token=%s | credits=%d",
                            credit_achat.id, token, credit_achat.credits_achetes,
                        )
        elif status_pay == "canceled":
            paiement_updated = Paiement.objects.filter(
                token_paydunya=token, statut=Paiement.Statut.EN_ATTENTE
            ).update(statut=Paiement.Statut.ECHOUE)
            if paiement_updated:
                logger.info("PAIEMENT_ANNULE | token=%s", token)
            else:
                CreditAchat.objects.filter(
                    token_paydunya=token, statut=CreditAchat.Statut.EN_ATTENTE
                ).update(statut=CreditAchat.Statut.ECHOUE)
                logger.info("CREDIT_ACHAT_ANNULE | token=%s", token)

        return Response({"ok": True})


class VerifierPaiementView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, token):
        paiement = generics.get_object_or_404(
            Paiement, token_paydunya=token, parent=request.user
        )

        from backends.paiement.paydunya import confirmer_paiement

        try:
            succes, response = confirmer_paiement(token)
            if succes:
                paydunya_status = response.get("status")
                if paydunya_status == "completed" and paiement.statut != Paiement.Statut.COMPLETE:
                    paiement.statut = Paiement.Statut.COMPLETE
                    paiement.receipt_url = response.get("receipt_url", "")
                    paiement.save(update_fields=["statut", "receipt_url"])
                elif paydunya_status == "canceled":
                    paiement.statut = Paiement.Statut.ECHOUE
                    paiement.save(update_fields=["statut"])
        except Exception:
            logger.exception("VERIFIER_PAIEMENT_ERREUR | token=%s", token)

        return Response(PaiementSerializer(paiement).data)


class HistoriquePaiementsView(generics.ListAPIView):
    serializer_class = PaiementSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.PARENT:
            return Paiement.objects.filter(parent=user).select_related("encadreur__user")
        return Paiement.objects.filter(encadreur__user=user).select_related("parent")


class CreditStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        parent = request.user
        total_achetes = CreditAchat.objects.filter(
            parent=parent, statut=CreditAchat.Statut.COMPLETE
        ).aggregate(total=models.Sum("credits_achetes"))["total"] or 0
        total_utilises = CreditUtilisation.objects.filter(parent=parent).count()
        credits_restants = max(0, total_achetes - total_utilises)
        debloque_ids = list(
            CreditUtilisation.objects.filter(parent=parent).values_list("encadreur_id", flat=True)
        )
        return Response({
            "credits_restants": credits_restants,
            "total_achetes": total_achetes,
            "total_utilises": total_utilises,
            "debloque_ids": debloque_ids,
        })


class InitierAchatCreditsView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsParent)

    def post(self, request):
        from backends.paiement.paydunya import creer_facture

        montant = 1000
        credits = 3
        parent_nom = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email

        credit_achat = CreditAchat.objects.create(
            parent=request.user,
            credits_achetes=credits,
            montant=montant,
        )

        try:
            succes, response = creer_facture(
                montant=montant,
                description="Achat de 3 crédits de contact MYCD",
                parent_nom=parent_nom,
                parent_email=request.user.email,
                parent_phone=request.user.phone,
                credit_achat_id=credit_achat.id,
            )

            if succes:
                credit_achat.token_paydunya = response.get("token", "")
                credit_achat.receipt_url = response.get("receipt_url", "")
                credit_achat.save(update_fields=["token_paydunya", "receipt_url"])
                logger.info(
                    "CREDIT_ACHAT_INITIE | id=%d | montant=%d | token=%s",
                    credit_achat.id, montant, credit_achat.token_paydunya,
                )
                return Response({
                    "credit_achat_id": credit_achat.id,
                    "invoice_url": response.get("response_text"),
                })
            else:
                credit_achat.statut = CreditAchat.Statut.ECHOUE
                credit_achat.save(update_fields=["statut"])
                logger.warning(
                    "CREDIT_ACHAT_ECHEC | id=%d | response=%s",
                    credit_achat.id, response,
                )
                return Response(
                    {"detail": "Erreur lors de la création de la facture PayDunya"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
        except Exception:
            credit_achat.statut = CreditAchat.Statut.ECHOUE
            credit_achat.save(update_fields=["statut"])
            logger.exception("CREDIT_ACHAT_EXCEPTION | id=%d", credit_achat.id)
            return Response(
                {"detail": "Erreur lors de la communication avec PayDunya"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class DebloquerEncadreurView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsParent)

    def post(self, request, encadreur_pk):
        encadreur_profil = generics.get_object_or_404(ProfilEncadreur, id=encadreur_pk)

        if a_debloque_encadreur(request.user, encadreur_profil):
            conversation, _ = Conversation.objects.get_or_create(
                parent=request.user,
                encadreur=encadreur_profil.user,
            )
            return Response({
                "conversation_id": conversation.id,
                "credit_consomme": False,
            })

        with transaction.atomic():
            unlocked_before = CreditUtilisation.objects.filter(
                parent=request.user, encadreur=encadreur_profil
            ).exists()
            if unlocked_before:
                conversation, _ = Conversation.objects.get_or_create(
                    parent=request.user,
                    encadreur=encadreur_profil.user,
                )
                return Response({
                    "conversation_id": conversation.id,
                    "credit_consomme": False,
                })

            credit_achats = list(
                CreditAchat.objects.filter(
                    parent=request.user, statut=CreditAchat.Statut.COMPLETE
                ).select_for_update()
            )
            total_achetes = sum(ca.credits_achetes for ca in credit_achats)
            total_utilises = CreditUtilisation.objects.filter(parent=request.user).count()
            if total_achetes - total_utilises <= 0:
                return Response(
                    {"detail": "Crédits insuffisants. Achetez des crédits pour contacter cet encadreur.",
                     "code": "credits_insuffisants"},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

            CreditUtilisation.objects.create(
                parent=request.user,
                encadreur=encadreur_profil,
            )

            conversation, _ = Conversation.objects.get_or_create(
                parent=request.user,
                encadreur=encadreur_profil.user,
            )

        Notification.objects.create(
            user=encadreur_profil.user,
            type=Notification.Type.NEW_MESSAGE,
            title=f"{request.user.first_name or request.user.email} vous a débloqué",
            message=f"Un parent a utilisé un crédit pour vous contacter.",
            link=f"/messagerie/{conversation.id}",
        )

        logger.info(
            "ENCADREUR_DEBLOQUE | Parent=%s (id=%d) | Encadreur=%s (id=%d) | Conversation=%d",
            request.user.email, request.user.id,
            encadreur_profil.user.email, encadreur_profil.id,
            conversation.id,
        )

        return Response({
            "conversation_id": conversation.id,
            "credit_consomme": True,
        })
