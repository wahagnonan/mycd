from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backends.avis.models import Avis
from backends.notifications.models import Notification


def _recalculer_notes(encadreur):
    agg = Avis.objects.filter(encadreur=encadreur).aggregate(
        moyenne=Avg("note"), total=Count("id")
    )
    encadreur.note_moyenne = round(agg["moyenne"] or 0.0, 1)
    encadreur.nombre_avis = agg["total"] or 0
    encadreur.save(update_fields=["note_moyenne", "nombre_avis"])


@receiver(post_save, sender=Avis)
def avis_post_save(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.encadreur.user,
            type=Notification.Type.NEW_REVIEW,
            title=f"Nouvel avis de {instance.parent.email}",
            message=f"Note : {instance.note}/5" + (f" — {instance.commentaire[:100]}" if instance.commentaire else ""),
            link=f"/encadreurs/{instance.encadreur.id}",
        )
    _recalculer_notes(instance.encadreur)


@receiver(post_delete, sender=Avis)
def avis_post_delete(sender, instance, **kwargs):
    _recalculer_notes(instance.encadreur)
