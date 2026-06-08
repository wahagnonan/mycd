import hmac
import hashlib
import json
import logging

from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backends.accounts.permissions import IsParent
from backends.encadreurs.models import ProfilEncadreur
from backends.paiement.models import CreditAchat

logger = logging.getLogger(__name__)


def _mask_token(token: str) -> str:
    if len(token) > 8:
        return token[:6] + "..."
    return token


def _mask_email(email: str) -> str:
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 1:
            return local[0] + "***@" + domain
        return local + "***@" + domain
    return email


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
            logger.warning("PAIEMENT_CALLBACK_HASH_INVALIDE")
            return Response({"detail": "Hash invalide"}, status=status.HTTP_403_FORBIDDEN)

        status_pay = body.get("status")
        token = body.get("invoice", {}).get("token", "")
        receipt_url = body.get("receipt_url", "")

        if not token:
            logger.warning("PAIEMENT_CALLBACK_SANS_TOKEN")
            return Response({"detail": "Token manquant"}, status=status.HTTP_400_BAD_REQUEST)

        if status_pay == "completed":
            with transaction.atomic():
                credit_achat = CreditAchat.objects.filter(
                    token_paydunya=token, statut=CreditAchat.Statut.EN_ATTENTE
                ).select_for_update().first()

                if not credit_achat:
                    logger.info(
                        "CREDIT_ACHAT_CALLBACK_IGNORE | token=%s",
                        _mask_token(token),
                    )
                    return Response({"ok": True})

                invoice_amount = body.get("amount") or body.get("invoice", {}).get("total_amount")
                if invoice_amount is not None and invoice_amount != credit_achat.montant:
                    logger.warning(
                        "CREDIT_ACHAT_MONTANT_INVALIDE | id=%d | attendu=%d | recu=%s",
                        credit_achat.id, credit_achat.montant, invoice_amount,
                    )
                    return Response({"detail": "Montant invalide"}, status=status.HTTP_400_BAD_REQUEST)

                credit_achat.statut = CreditAchat.Statut.COMPLETE
                credit_achat.receipt_url = receipt_url
                credit_achat.save(update_fields=["statut", "receipt_url"])

                Notification.objects.create(
                    user=credit_achat.parent,
                    type=Notification.Type.PAYMENT_RECEIVED,
                    title="Achat de crédits réussi",
                    message=f"Vous avez acheté {credit_achat.credits_achetes} crédits de contact.",
                    link="/encadreurs",
                )
                logger.info(
                    "CREDIT_ACHAT_COMPLETE | id=%d | token=%s | credits=%d",
                    credit_achat.id, _mask_token(token), credit_achat.credits_achetes,
                )
        elif status_pay == "canceled":
            CreditAchat.objects.filter(
                token_paydunya=token, statut=CreditAchat.Statut.EN_ATTENTE
            ).update(statut=CreditAchat.Statut.ECHOUE)
            logger.info("CREDIT_ACHAT_ANNULE | token=%s", _mask_token(token))

        return Response({"ok": True})


class CreditStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        from backends.paiement.helpers import get_credit_summary

        parent = request.user
        summary = get_credit_summary(parent)
        return Response(summary)


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
                    credit_achat.id, montant, _mask_token(credit_achat.token_paydunya),
                )
                return Response({
                    "credit_achat_id": credit_achat.id,
                    "invoice_url": response.get("response_text"),
                })
            else:
                credit_achat.statut = CreditAchat.Statut.ECHOUE
                credit_achat.save(update_fields=["statut"])
                logger.warning(
                    "CREDIT_ACHAT_ECHEC | id=%d",
                    credit_achat.id,
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
        from backends.paiement.services import consume_credit

        encadreur_profil = generics.get_object_or_404(ProfilEncadreur, id=encadreur_pk)

        if not encadreur_profil.disponible:
            return Response(
                {"detail": "Cet encadreur n'est actuellement pas disponible.", "code": "non_disponible"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not encadreur_profil.verified:
            return Response(
                {"detail": "Cet encadreur n'a pas encore été vérifié.", "code": "non_verifie"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not encadreur_profil.questionnaire_rempli:
            return Response(
                {"detail": "Cet encadreur n'a pas encore complété son profil.", "code": "profil_incomplet"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not encadreur_profil.cgu_acceptees:
            return Response(
                {"detail": "Cet encadreur n'a pas encore accepté les conditions.", "code": "cgu_non_acceptees"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = consume_credit(request.user, encadreur_profil)

        if "error" in result:
            return Response(
                {"detail": result["error"], "code": result.get("code", "")},
                status=result.get("status", status.HTTP_400_BAD_REQUEST),
            )

        logger.info(
            "ENCADREUR_DEBLOQUE | Parent=%s (id=%d) | Encadreur=%s (id=%d) | Conversation=%d",
            _mask_email(request.user.email), request.user.id,
            _mask_email(encadreur_profil.user.email), encadreur_profil.id,
            result["conversation_id"],
        )

        return Response({
            "conversation_id": result["conversation_id"],
            "credit_consomme": result["credit_consomme"],
        })
