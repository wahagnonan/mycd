from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


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
