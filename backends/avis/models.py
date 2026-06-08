from django.core.exceptions import ValidationError
from django.db import models

from backends.accounts.models import User
from backends.encadreurs.models import ProfilEncadreur


class Avis(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avis_donnes")
    encadreur = models.ForeignKey(
        ProfilEncadreur, on_delete=models.CASCADE, related_name="avis_recus"
    )
    note = models.PositiveSmallIntegerField(help_text="Note de 1 à 5")
    commentaire = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "avis"
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ("parent", "encadreur")
        ordering = ("-created_at",)

    def clean(self):
        if self.note < 1 or self.note > 5:
            raise ValidationError({"note": "La note doit être comprise entre 1 et 5."})

    def __str__(self):
        return f"Avis de {self.parent.email} - {self.note}/5"
