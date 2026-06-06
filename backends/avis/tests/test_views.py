import pytest
from django.urls import reverse
from rest_framework import status


class TestAvisCreateView:
    def test_parent_can_create_avis(self, parent_client, encadreur_profile):
        url = reverse("avis-create", args=[encadreur_profile.id])
        data = {"note": 5, "commentaire": "Excellent encadreur"}
        response = parent_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["note"] == 5
        assert response.data["parent_email"] == "parent@test.com"

    def test_create_avis_anonymous(self, api_client, encadreur_profile):
        url = reverse("avis-create", args=[encadreur_profile.id])
        data = {"note": 4}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_encadreur_cannot_create_avis(self, auth_client, encadreur_profile):
        url = reverse("avis-create", args=[encadreur_profile.id])
        data = {"note": 5}
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_avis_invalid_note(self, parent_client, encadreur_profile):
        url = reverse("avis-create", args=[encadreur_profile.id])
        data = {"note": 6}
        response = parent_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_avis_encadreur_not_found(self, parent_client):
        url = reverse("avis-create", args=[99999])
        data = {"note": 4}
        response = parent_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAvisByEncadreurView:
    def test_list_public(self, api_client, encadreur_profile, parent_user):
        from backends.avis.models import Avis
        Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=5)
        url = reverse("avis-list", args=[encadreur_profile.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["note"] == 5

    def test_list_empty(self, api_client, encadreur_profile):
        url = reverse("avis-list", args=[encadreur_profile.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_multiple_avis(self, api_client, encadreur_profile, parent_user):
        from backends.accounts.models import User
        from backends.avis.models import Avis
        from model_bakery import baker
        parent2 = baker.make(User, email="p2@test.com", phone="+2250606060606", role=User.Role.PARENT)
        Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=5)
        Avis.objects.create(parent=parent2, encadreur=encadreur_profile, note=3)
        url = reverse("avis-list", args=[encadreur_profile.id])
        response = api_client.get(url)
        assert len(response.data) == 2


class TestAvisDetailView:
    def test_owner_can_update(self, parent_client, encadreur_profile, parent_user):
        from backends.avis.models import Avis
        avis = Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=4)
        url = reverse("avis-detail", args=[encadreur_profile.id, avis.id])
        response = parent_client.patch(url, {"note": 3}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["note"] == 3

    def test_owner_can_delete(self, parent_client, encadreur_profile, parent_user):
        from backends.avis.models import Avis
        avis = Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=4)
        url = reverse("avis-detail", args=[encadreur_profile.id, avis.id])
        response = parent_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_other_user_cannot_update(self, auth_client, encadreur_profile, parent_user):
        from backends.avis.models import Avis
        avis = Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=4)
        url = reverse("avis-detail", args=[encadreur_profile.id, avis.id])
        response = auth_client.patch(url, {"note": 1}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
