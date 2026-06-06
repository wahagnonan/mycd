from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("backends.core.urls")),
    path("api/", include("backends.accounts.urls")),
    path("api/", include("backends.encadreurs.urls")),
    path("api/", include("backends.messagerie.urls")),
    path("api/", include("backends.notifications.urls")),
    path("api/", include("backends.avis.urls")),
    path("api/", include("backends.paiement.urls")),
]
