from django.contrib import admin

from backends.avis.models import Avis


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ("parent", "encadreur", "note", "created_at")
    list_filter = ("note", "created_at")
    search_fields = ("parent__email", "encadreur__user__email", "commentaire")
