import pytest
from django.urls import reverse
from rest_framework import status


class TestEncadreurListView:
    LIST_URL = reverse("encadreur-list")

    def test_list_public(self, api_client, encadreur_with_matieres):
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_list_pagination(self, api_client, encadreur_with_matieres):
        response = api_client.get(self.LIST_URL)
        assert "results" in response.data
        assert "count" in response.data
        assert "next" in response.data

    def test_list_filters_disponible_only(self, api_client, db):
        from backends.accounts.models import User
        from backends.encadreurs.models import ProfilEncadreur
        from model_bakery import baker
        user1 = baker.make(User, email="d1@test.com", phone="+2250101010101", role=User.Role.ENCADREUR)
        user2 = baker.make(User, email="d2@test.com", phone="+2250202020202", role=User.Role.ENCADREUR)
        ProfilEncadreur.objects.create(user=user1, disponible=True)
        ProfilEncadreur.objects.create(user=user2, disponible=False)
        response = api_client.get(self.LIST_URL)
        for result in response.data["results"]:
            assert result["email"] != "d2@test.com"

    def test_filter_by_ville(self, api_client, encadreur_with_matieres):
        encadreur_with_matieres.user.ville = "Abidjan"
        encadreur_with_matieres.user.save()
        response = api_client.get(self.LIST_URL, {"ville": "Abidjan"})
        assert response.data["count"] >= 1

    def test_filter_by_ville_no_match(self, api_client, encadreur_with_matieres):
        encadreur_with_matieres.user.ville = "Abidjan"
        encadreur_with_matieres.user.save()
        response = api_client.get(self.LIST_URL, {"ville": "Yamoussoukro"})
        assert response.data["count"] == 0

    def test_filter_by_matiere(self, api_client, encadreur_with_matieres, matieres):
        matiere = matieres[0]
        response = api_client.get(self.LIST_URL, {"matiere": matiere.id})
        assert response.data["count"] >= 1

    def test_filter_by_matiere_no_match(self, api_client, encadreur_with_matieres):
        response = api_client.get(self.LIST_URL, {"matiere": 99999})
        assert response.data["count"] == 0

    def test_search_by_name(self, api_client, encadreur_with_matieres):
        encadreur_with_matieres.user.first_name = "Jean"
        encadreur_with_matieres.user.last_name = "Dupont"
        encadreur_with_matieres.user.save()
        response = api_client.get(self.LIST_URL, {"search": "Dupont"})
        assert response.data["count"] >= 1

    def test_search_no_match(self, api_client, encadreur_with_matieres):
        response = api_client.get(self.LIST_URL, {"search": "Inexistant"})
        assert response.data["count"] == 0

    def test_filter_by_matiere_nom(self, api_client, encadreur_with_matieres):
        encadreur_with_matieres.autre_matiere = "Arabe"
        encadreur_with_matieres.save()
        response = api_client.get(self.LIST_URL, {"matiere_nom": "Arabe"})
        assert response.data["count"] >= 1

    def test_filter_by_matiere_nom_partial(self, api_client, encadreur_with_matieres):
        encadreur_with_matieres.autre_matiere = "Arabe littéraire"
        encadreur_with_matieres.save()
        response = api_client.get(self.LIST_URL, {"matiere_nom": "Arabe"})
        assert response.data["count"] >= 1


class TestEncadreurDetailView:
    def test_detail_public(self, api_client, encadreur_with_matieres):
        url = reverse("encadreur-detail", args=[encadreur_with_matieres.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "encadreur@test.com"

    def test_detail_not_found(self, api_client):
        url = reverse("encadreur-detail", args=[99999])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMonProfilView:
    PROFIL_URL = reverse("mon-profil")

    def test_get_profile(self, auth_client):
        response = auth_client.get(self.PROFIL_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "encadreur@test.com"

    def test_get_profile_anonymous(self, api_client):
        response = api_client.get(self.PROFIL_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client):
        data = {"bio": "Nouvelle bio"}
        response = auth_client.patch(self.PROFIL_URL, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "Nouvelle bio"

    def test_parent_cannot_access(self, parent_client):
        response = parent_client.get(self.PROFIL_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMatiereListView:
    LIST_URL = reverse("matiere-list")

    def test_list_public(self, api_client, matieres):
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_list_no_authentication(self, api_client):
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
