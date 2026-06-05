from django.urls import path

from backends.accounts.views import (
    LoginView,
    MeView,
    RegisterView,
    TokenRefreshView,
    api_root,
)

urlpatterns = [
    path("", api_root, name="api-root"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
]
