from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backends.avis.models import Avis


def _recalculer_notes(encadreur):
    agg = Avis.objects.filter(encadreur=encadreur).aggregate(
        moyenne=Avg("note"), total=Count("id")
    )
    encadreur.note_moyenne = round(agg["moyenne"] or 0.0, 1)
    encadreur.nombre_avis = agg["total"] or 0
    encadreur.save(update_fields=["note_moyenne", "nombre_avis"])


@receiver(post_save, sender=Avis)
def avis_post_save(sender, instance, **kwargs):
    _recalculer_notes(instance.encadreur)


@receiver(post_delete, sender=Avis)
def avis_post_delete(sender, instance, **kwargs):
    _recalculer_notes(instance.encadreur)
