import logging

from django.db import models
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .models import Avis, Conversation, Matiere, Message, Notification, ProfilEncadreur, User
from .serializers import (
    AvisSerializer,
    ConversationListSerializer,
    CreateConversationSerializer,
    LoginSerializer,
    MatiereSerializer,
    MessageSerializer,
    NotificationSerializer,
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


class IsParent(permissions.BasePermission):
    """Seuls les parents peuvent effectuer cette action."""

    message = "Seuls les parents peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.PARENT
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
    et filtres avancés : ville, quartier, matière, recherche texte,
    note minimum, niveau d'études, niveaux d'enseignement,
    tarif max, jours disponibles, tri.
    """
    serializer_class = ProfilEncadreurSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        qs = ProfilEncadreur.objects.filter(disponible=True).select_related("user")

        # Recherche texte
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                models.Q(user__first_name__icontains=search)
                | models.Q(user__last_name__icontains=search)
                | models.Q(bio__icontains=search)
            )

        # Ville / quartier
        ville = self.request.query_params.get("ville")
        if ville:
            qs = qs.filter(user__ville__icontains=ville)
        quartier = self.request.query_params.get("quartier")
        if quartier:
            qs = qs.filter(user__quartier__icontains=quartier)

        # Matière
        matiere = self.request.query_params.get("matiere")
        if matiere:
            qs = qs.filter(matieres__id=matiere)

        # Note minimum
        note_min = self.request.query_params.get("note_min")
        if note_min:
            try:
                qs = qs.filter(note_moyenne__gte=float(note_min))
            except ValueError:
                pass

        # Niveau d'études
        niveau_etudes = self.request.query_params.get("niveau_etudes")
        if niveau_etudes:
            qs = qs.filter(niveau_etudes=niveau_etudes)

        # Niveaux d'enseignement (JSONField — un ou plusieurs)
        niveaux_ens = self.request.query_params.getlist("niveaux_enseignement")
        for niv in niveaux_ens:
            qs = qs.filter(niveaux_enseignement__contains=niv)

        # Jours disponibles (JSONField)
        jours = self.request.query_params.getlist("jours_disponibles")
        for jour in jours:
            qs = qs.filter(jours_disponibles__contains=jour)

        # Tarif max mensuel
        tarif_max_mois = self.request.query_params.get("tarif_max_mois")
        if tarif_max_mois:
            try:
                qs = qs.filter(
                    models.Q(tarif_mois__lte=int(tarif_max_mois))
                    | models.Q(tarif_mois__isnull=True)
                )
            except ValueError:
                pass

        # Tarif max horaire
        tarif_max_horaire = self.request.query_params.get("tarif_max_horaire")
        if tarif_max_horaire:
            try:
                qs = qs.filter(
                    models.Q(tarif_horaire__lte=int(tarif_max_horaire))
                    | models.Q(tarif_horaire__isnull=True)
                )
            except ValueError:
                pass

        # Tri
        ordering = self.request.query_params.get("ordering")
        if ordering in ("note", "-note", "tarif_mois", "-tarif_mois",
                         "tarif_horaire", "-tarif_horaire",
                         "date_inscription", "-date_inscription"):
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-date_inscription")

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


# ─── Messagerie ─────────────────────────────────────────────

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            models.Q(parent=user) | models.Q(encadreur=user)
        ).select_related("parent", "encadreur")


class CreateConversationView(generics.CreateAPIView):
    serializer_class = CreateConversationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        encadreur = User.objects.get(id=serializer.validated_data["encadreur_id"])
        conversation, created = Conversation.objects.get_or_create(
            parent=request.user,
            encadreur=encadreur,
        )
        if created:
            logger.info(
                "CONVERSATION_CREATED | Parent=%s (id=%d) | Encadreur=%s (id=%d)",
                request.user.email, request.user.id,
                encadreur.email, encadreur.id,
            )
        return Response({"id": conversation.id, "created": created})


class ConversationMessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        conv = Conversation.objects.get(id=self.kwargs["pk"])
        user = self.request.user
        if user not in (conv.parent, conv.encadreur):
            return Message.objects.none()
        return Message.objects.filter(conversation=conv).select_related("sender")

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(id=self.kwargs["pk"])
        user = self.request.user
        if user not in (conversation.parent, conversation.encadreur):
            raise PermissionDenied("Vous ne participez pas à cette conversation")
        msg = serializer.save(conversation=conversation, sender=user)
        destinataire = conversation.encadreur if user == conversation.parent else conversation.parent
        Notification.objects.create(
            user=destinataire,
            type=Notification.Type.NEW_MESSAGE,
            title=f"Nouveau message de {user.first_name or user.email}",
            message=msg.content[:100],
            link=f"/messagerie/{conversation.id}",
        )
        logger.info(
            "MESSAGE_SENT | Conversation=%d | Sender=%s (id=%d)",
            conversation.id, user.email, user.id,
        )


class MarkAsReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        conversation = Conversation.objects.get(id=pk)
        user = request.user
        if user not in (conversation.parent, conversation.encadreur):
            raise PermissionDenied("Vous ne participez pas à cette conversation")
        updated = conversation.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
        return Response({"marques_lus": updated})


# ─── Notifications ─────────────────────────────────────────

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response({"ok": True})


class MarkAllNotificationsReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"marques_lus": updated})


# ─── Avis ────────────────────────────────────────────────────

class AvisCreateView(generics.CreateAPIView):
    serializer_class = AvisSerializer
    permission_classes = (permissions.IsAuthenticated, IsParent)

    def perform_create(self, serializer):
        encadreur_id = self.kwargs["encadreur_pk"]
        encadreur = generics.get_object_or_404(ProfilEncadreur, id=encadreur_id)
        serializer.save(parent=self.request.user, encadreur=encadreur)
        logger.info(
            "AVIS_CREATED | Parent=%s (id=%d) | Encadreur=%s (id=%d) | Note=%d",
            self.request.user.email, self.request.user.id,
            encadreur.user.email, encadreur.id,
            serializer.validated_data["note"],
        )


class AvisByEncadreurView(generics.ListAPIView):
    serializer_class = AvisSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return Avis.objects.filter(
            encadreur_id=self.kwargs["encadreur_pk"]
        ).select_related("parent")


class AvisDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AvisSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Avis.objects.filter(parent=self.request.user)
