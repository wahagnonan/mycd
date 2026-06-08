import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

sys.path = [p for p in sys.path if not p.endswith("backends")]

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backends.backends.settings")
os.environ.setdefault("PAYDUNYA_MASTER_KEY", "test_master_key")
os.environ.setdefault("PAYDUNYA_PRIVATE_KEY", "test_private_key")
os.environ.setdefault("PAYDUNYA_TOKEN", "test_token")
os.environ.setdefault("PAYDUNYA_MODE", "test")
os.environ.setdefault("DJANGO_DEBUG", "False")

from django.conf import settings

settings.SECURE_SSL_REDIRECT = False

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client(db):
    return APIClient()


@pytest.fixture
def auth_client(api_client, encadreur_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(encadreur_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def parent_user(db):
    from model_bakery import baker
    from backends.accounts.models import User
    return baker.make(
        User,
        email="parent@test.com",
        phone="+2250101010101",
        role=User.Role.PARENT,
        first_name="Parent",
        last_name="Test",
    )


@pytest.fixture
def parent_client(api_client, parent_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(parent_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def encadreur_user(db):
    from model_bakery import baker
    from backends.accounts.models import User
    return baker.make(
        User,
        email="encadreur@test.com",
        phone="+2250202020202",
        role=User.Role.ENCADREUR,
        first_name="Encadreur",
        last_name="Test",
    )


@pytest.fixture
def encadreur_profile(encadreur_user):
    from backends.encadreurs.models import ProfilEncadreur
    return ProfilEncadreur.objects.create(user=encadreur_user)


@pytest.fixture
def matiere(db):
    from backends.encadreurs.models import Matiere
    return Matiere.objects.create(nom="Mathématiques")


@pytest.fixture
def matieres(db):
    from backends.encadreurs.models import Matiere
    noms = ["Mathématiques", "Français", "Anglais", "Physique", "SVT"]
    return [Matiere.objects.create(nom=nom) for nom in noms]


@pytest.fixture
def encadreur_with_matieres(encadreur_profile, matieres):
    encadreur_profile.matieres.set(matieres)
    encadreur_profile.bio = "Encadreur expérimenté"
    encadreur_profile.tarif_mois = 50000
    encadreur_profile.disponible = True
    encadreur_profile.save()
    return encadreur_profile
