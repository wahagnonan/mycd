from rest_framework import permissions

from backends.accounts.models import User


class IsEncadreur(permissions.BasePermission):
    message = "Seuls les encadreurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.ENCADREUR
        )


class IsParent(permissions.BasePermission):
    message = "Seuls les parents peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.PARENT
        )
