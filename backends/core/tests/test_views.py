import pytest
from django.urls import reverse
from rest_framework import status


class TestVilleListView:
    VILLES_URL = reverse("ville-list")

    def test_villes_public(self, api_client):
        response = api_client.get(self.VILLES_URL)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0

    def test_villes_structure(self, api_client):
        response = api_client.get(self.VILLES_URL)
        ville = response.data[0]
        assert "ville" in ville
        assert "quartiers" in ville
        assert isinstance(ville["quartiers"], list)

    def test_villes_contains_abidjan(self, api_client):
        response = api_client.get(self.VILLES_URL)
        villes = [v["ville"] for v in response.data]
        assert "Abidjan" in villes

    def test_villes_contains_autre(self, api_client):
        response = api_client.get(self.VILLES_URL)
        villes = [v["ville"] for v in response.data]
        assert "Autre" in villes

    def test_villes_no_auth_required(self, api_client):
        response = api_client.get(self.VILLES_URL)
        assert response.status_code == status.HTTP_200_OK
