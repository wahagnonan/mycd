from django.conf import settings
from django.conf.urls.static import static
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
