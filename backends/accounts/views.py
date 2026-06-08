import logging

from django.contrib.auth import authenticate
from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from backends.accounts.models import User
from backends.accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from backends.encadreurs.models import ProfilEncadreur

logger = logging.getLogger(__name__)


def _mask_email(email: str) -> str:
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 1:
            return local[0] + "***@" + domain
        return local + "***@" + domain
    return email


class LoginThrottle(AnonRateThrottle):
    scope = "login"


class RegisterThrottle(AnonRateThrottle):
    scope = "register"


class RefreshThrottle(AnonRateThrottle):
    scope = "refresh"


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
    throttle_classes = [RegisterThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
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
                _mask_email(serializer.validated_data["email"]),
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
