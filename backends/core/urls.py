from django.urls import path

from backends.core.views import ville_list

urlpatterns = [
    path("villes/", ville_list, name="ville-list"),
]
