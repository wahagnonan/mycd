from django.db import models

from backends.accounts.models import User
from backends.encadreurs.models import ProfilEncadreur


class Paiement(models.Model):
    class TypePaiement(models.TextChoices):
        COURS_MOIS = "cours_mois", "Cours au mois"
        COURS_HORAIRE = "cours_horaire", "Cours à l'heure"

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        COMPLETE = "complete", "Complété"
        ECHOUE = "echoue", "Échoué"
        REMBOURSE = "rembourse", "Remboursé"

    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="paiements_emis"
    )
    encadreur = models.ForeignKey(
        ProfilEncadreur, on_delete=models.CASCADE, related_name="paiements_recus"
    )
    montant = models.PositiveIntegerField(help_text="Montant en FCFA")
    type = models.CharField(
        max_length=20, choices=TypePaiement.choices, default=TypePaiement.COURS_MOIS
    )
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    token_paydunya = models.CharField(max_length=100, blank=True, default="")
    receipt_url = models.URLField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "paiement"
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Paiement {self.id} — {self.montant} FCFA ({self.statut})"


class CreditAchat(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        COMPLETE = "complete", "Complété"
        ECHOUE = "echoue", "Échoué"

    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credit_achats")
    credits_achetes = models.PositiveIntegerField(default=3)
    montant = models.PositiveIntegerField(help_text="Montant payé en FCFA")
    token_paydunya = models.CharField(max_length=100, blank=True, default="")
    receipt_url = models.URLField(blank=True, default="")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "paiement"
        ordering = ("-created_at",)
        verbose_name = "Achat de crédits"
        verbose_name_plural = "Achats de crédits"

    def __str__(self):
        return f"CreditAchat {self.id} — {self.parent.email} ({self.credits_achetes} crédits, {self.statut})"


class CreditUtilisation(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credits_utilises")
    encadreur = models.ForeignKey(
        ProfilEncadreur, on_delete=models.CASCADE, related_name="credits_consommes"
    )
    credit_achat = models.ForeignKey(
        CreditAchat, on_delete=models.SET_NULL, null=True, blank=True, related_name="utilisations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "paiement"
        unique_together = ("parent", "encadreur")
        verbose_name = "Utilisation de crédit"
        verbose_name_plural = "Utilisations de crédits"

    def __str__(self):
        return f"Crédit utilisé: {self.parent.email} → {self.encadreur.user.email}"


# Nouveaux alias métier (pointent vers les mêmes modèles)
CreditPurchase = CreditAchat
ContactUnlock = CreditUtilisation
