from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Matiere, ProfilEncadreur, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "phone", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations", {"fields": ("phone", "role", "ville", "quartier")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "password1", "password2", "role"),
        }),
    )
    search_fields = ("email", "phone")
    ordering = ("email",)


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(ProfilEncadreur)
class ProfilEncadreurAdmin(admin.ModelAdmin):
    list_display = ("user", "note_moyenne", "verified", "disponible")
    list_filter = ("verified", "disponible", "matieres")
    search_fields = ("user__email",)
