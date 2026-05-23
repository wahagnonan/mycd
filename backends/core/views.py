import logging

from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .models import ProfilEncadreur, User, Matiere
from .serializers import (
    LoginSerializer,
    MatiereSerializer,
    ProfilEncadreurSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


# ─── Throttles ──────────────────────────────────────────────

class LoginThrottle(AnonRateThrottle):
    scope = "login"


class RefreshThrottle(AnonRateThrottle):
    scope = "refresh"


class MonProfilThrottle(UserRateThrottle):
    """Throttle générique pour /api/mon-profil/"""
    scope = "mon-profil"


class MonProfilPatchThrottle(UserRateThrottle):
    """Throttle plus restrictif pour les PATCH sur /api/mon-profil/"""
    scope = "mon-profil-patch"


# ─── Permissions ────────────────────────────────────────────

class IsEncadreur(permissions.BasePermission):
    """Seuls les utilisateurs avec le rôle 'encadreur' sont autorisés."""

    message = "Seuls les encadreurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.ENCADREUR
        )


# ─── Vues ───────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_root(request):
    return Response({
        "name": "MYCD API",
        "version": "1.0",
        "endpoints": {
            "register": "/api/auth/register/",
            "login": "/api/auth/login/",
            "refresh": "/api/auth/refresh/",
            "me": "/api/auth/me/",
            "encadreurs": "/api/encadreurs/",
            "mon-profil": "/api/mon-profil/",
            "matieres": "/api/matieres/",
        },
    })


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            logger.warning(
                "REGISTER_FAILED | IP=%s | Data=%s | Errors=%s",
                request.META.get("REMOTE_ADDR"),
                {k: v for k, v in request.data.items() if k not in ("password", "password2")},
                dict(serializer.errors),
            )
            raise
        user = serializer.save()
        if user.role == User.Role.ENCADREUR:
            ProfilEncadreur.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if not user:
            logger.info(
                "LOGIN_FAILED | IP=%s | Email=%s",
                request.META.get("REMOTE_ADDR"),
                serializer.validated_data["email"],
            )
            return Response(
                {"detail": "Email ou mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "Compte désactivé"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class TokenRefreshView(BaseTokenRefreshView):
    """Refresh token avec rate limiting et logs."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = [RefreshThrottle]

    def post(self, request, *args, **kwargs):
        logger.info(
            "TOKEN_REFRESH | IP=%s",
            request.META.get("REMOTE_ADDR"),
        )
        return super().post(request, *args, **kwargs)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class EncadreurListView(generics.ListAPIView):
    """
    Liste publique des encadreurs avec pagination (20/page)
    et filtres par ville, quartier, matière.
    """
    queryset = ProfilEncadreur.objects.filter(disponible=True).select_related("user").order_by("-date_inscription")
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        qs = super().get_queryset()
        ville = self.request.query_params.get("ville")
        quartier = self.request.query_params.get("quartier")
        matiere = self.request.query_params.get("matiere")
        if ville:
            qs = qs.filter(user__ville__icontains=ville)
        if quartier:
            qs = qs.filter(user__quartier__icontains=quartier)
        if matiere:
            qs = qs.filter(matieres__id=matiere)
        return qs


class EncadreurDetailView(generics.RetrieveAPIView):
    queryset = ProfilEncadreur.objects.select_related("user")
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.AllowAny,)


class MonProfilView(generics.RetrieveUpdateAPIView):
    """
    Gestion du profil encadreur.
    - Accessible uniquement aux utilisateurs avec rôle='encadreur'
    - GET : 60 req/min
    - PATCH : 10 req/min
    - Création automatique du profil si inexistant
    """
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.IsAuthenticated, IsEncadreur)

    def get_throttles(self):
        if self.request.method == "PATCH":
            return [MonProfilPatchThrottle()]
        return [MonProfilThrottle()]

    def get_object(self):
        # Vérification redondante de sécurité (au cas où la permission class faiblit)
        if self.request.user.role != User.Role.ENCADREUR:
            raise PermissionDenied("Seuls les encadreurs peuvent accéder à leur profil")
        profil, created = ProfilEncadreur.objects.get_or_create(user=self.request.user)
        if created:
            logger.info(
                "PROFIL_CREATED | User=%s (id=%d)",
                self.request.user.email, self.request.user.id,
            )
        return profil

    def perform_update(self, serializer):
        logger.info(
            "PROFIL_UPDATED | User=%s (id=%d)",
            self.request.user.email, self.request.user.id,
        )
        return super().perform_update(serializer)


class MatiereListView(generics.ListAPIView):
    queryset = Matiere.objects.all().order_by("nom")
    serializer_class = MatiereSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
