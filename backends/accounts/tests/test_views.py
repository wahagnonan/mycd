import pytest
from django.urls import reverse
from rest_framework import status

from backends.accounts.models import User
from backends.encadreurs.models import ProfilEncadreur


class TestApiRoot:
    def test_api_root(self, api_client):
        url = reverse("api-root")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "MYCD API"
        assert "register" in response.data["endpoints"]


class TestRegisterView:
    REGISTER_URL = reverse("register")

    def test_register_parent(self, api_client):
        data = {
            "email": "parent@test.com",
            "phone": "+2250101010101",
            "password": "secret123",
            "password2": "secret123",
            "role": User.Role.PARENT,
        }
        response = api_client.post(self.REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "parent@test.com"
        assert response.data["user"]["role"] == "parent"
        assert User.objects.count() == 1
        assert ProfilEncadreur.objects.count() == 0

    def test_register_encadreur_creates_profile(self, api_client):
        data = {
            "email": "encadreur@test.com",
            "phone": "+2250202020202",
            "password": "secret123",
            "password2": "secret123",
            "role": User.Role.ENCADREUR,
        }
        response = api_client.post(self.REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["role"] == "encadreur"
        assert ProfilEncadreur.objects.count() == 1
        profile = ProfilEncadreur.objects.first()
        assert profile.user.email == "encadreur@test.com"

    def test_register_password_mismatch(self, api_client):
        data = {
            "email": "parent@test.com",
            "phone": "+2250101010101",
            "password": "secret123",
            "password2": "different",
            "role": User.Role.PARENT,
        }
        response = api_client.post(self.REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client):
        data = {
            "email": "dup@test.com",
            "phone": "+2250101010101",
            "password": "secret123",
            "password2": "secret123",
            "role": User.Role.PARENT,
        }
        api_client.post(self.REGISTER_URL, data, format="json")
        response = api_client.post(self.REGISTER_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLoginView:
    LOGIN_URL = reverse("login")

    def test_login_success(self, api_client, encadreur_user):
        encadreur_user.set_password("secret123")
        encadreur_user.save()
        data = {"email": "encadreur@test.com", "password": "secret123"}
        response = api_client.post(self.LOGIN_URL, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "encadreur@test.com"

    def test_login_wrong_password(self, api_client, encadreur_user):
        data = {"email": "encadreur@test.com", "password": "wrong"}
        response = api_client.post(self.LOGIN_URL, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Email ou mot de passe incorrect" in response.data["detail"]

    def test_login_nonexistent_user(self, api_client):
        data = {"email": "nobody@test.com", "password": "secret123"}
        response = api_client.post(self.LOGIN_URL, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, api_client, db):
        from backends.accounts.models import User
        user = User.objects.create_user(
            email="inactive@test.com",
            password="secret123",
            phone="+2250505050505",
        )
        user.is_active = False
        user.save(update_fields=["is_active"])
        data = {"email": "inactive@test.com", "password": "secret123"}
        response = api_client.post(self.LOGIN_URL, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMeView:
    ME_URL = reverse("me")

    def test_me_authenticated(self, auth_client):
        response = auth_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "encadreur@test.com"
        assert response.data["role"] == "encadreur"

    def test_me_anonymous(self, api_client):
        response = api_client.get(self.ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
