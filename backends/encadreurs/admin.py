from django.contrib import admin

from backends.encadreurs.models import Matiere, ProfilEncadreur


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(ProfilEncadreur)
class ProfilEncadreurAdmin(admin.ModelAdmin):
    list_display = ("user", "note_moyenne", "verified", "disponible")
    list_filter = ("verified", "disponible", "matieres")
    search_fields = ("user__email",)
