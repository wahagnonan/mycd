from django.db import models

from backends.paiement.models import CreditAchat, CreditUtilisation


def get_credits_restants(parent):
    total_achetes = CreditAchat.objects.filter(
        parent=parent, statut=CreditAchat.Statut.COMPLETE
    ).aggregate(total=models.Sum("credits_achetes"))["total"] or 0
    total_utilises = CreditUtilisation.objects.filter(parent=parent).count()
    return total_achetes - total_utilises


def a_debloque_encadreur(parent, encadreur):
    return CreditUtilisation.objects.filter(parent=parent, encadreur=encadreur).exists()
