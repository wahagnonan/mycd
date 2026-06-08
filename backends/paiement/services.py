from django.db import transaction

from backends.messagerie.models import Conversation
from backends.notifications.models import Notification
from backends.paiement.helpers import a_debloque_encadreur
from backends.paiement.models import CreditAchat, CreditUtilisation


def consume_credit(parent, encadreur_profil):
    if a_debloque_encadreur(parent, encadreur_profil):
        conversation, _ = Conversation.objects.get_or_create(
            parent=parent,
            encadreur=encadreur_profil.user,
        )
        return {"conversation_id": conversation.id, "credit_consomme": False}

    with transaction.atomic():
        credit_achats = list(
            CreditAchat.objects.filter(
                parent=parent, statut=CreditAchat.Statut.COMPLETE
            ).select_for_update()
        )
        total_achetes = sum(ca.credits_achetes for ca in credit_achats)
        total_utilises = CreditUtilisation.objects.filter(parent=parent).count()
        if total_achetes - total_utilises <= 0:
            return {
                "error": "Crédits insuffisants. Achetez des crédits pour contacter cet encadreur.",
                "code": "credits_insuffisants",
                "status": 402,
            }

        usage = CreditUtilisation.objects.create(
            parent=parent,
            encadreur=encadreur_profil,
        )

        for ca in credit_achats:
            utilisations = ca.utilisations.count()
            if utilisations < ca.credits_achetes:
                usage.credit_achat = ca
                usage.save(update_fields=["credit_achat"])
                break

        conversation, _ = Conversation.objects.get_or_create(
            parent=parent,
            encadreur=encadreur_profil.user,
        )

    Notification.objects.create(
        user=encadreur_profil.user,
        type=Notification.Type.NEW_MESSAGE,
        title=f"{parent.first_name or parent.email} vous a débloqué",
        message="Un parent a utilisé un crédit pour vous contacter.",
        link=f"/messagerie/{conversation.id}",
    )

    return {"conversation_id": conversation.id, "credit_consomme": True}
