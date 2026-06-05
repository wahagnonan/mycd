from django.contrib import admin

from backends.paiement.models import CreditAchat, CreditUtilisation, Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("parent", "encadreur", "montant", "statut", "type", "created_at")
    list_filter = ("statut", "type", "created_at")
    search_fields = ("parent__email", "encadreur__user__email")


@admin.register(CreditAchat)
class CreditAchatAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "credits_achetes", "montant", "statut", "created_at")
    list_filter = ("statut",)
    search_fields = ("parent__email",)


@admin.register(CreditUtilisation)
class CreditUtilisationAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "encadreur", "created_at")
    list_filter = ("created_at",)
    search_fields = ("parent__email", "encadreur__user__email")
