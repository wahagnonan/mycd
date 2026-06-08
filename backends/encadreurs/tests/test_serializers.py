import pytest
from rest_framework.test import APIRequestFactory

from backends.encadreurs.serializers import (
    MatiereSerializer,
    ProfilEncadreurSerializer,
)
from backends.encadreurs.models import Matiere, ProfilEncadreur
from backends.accounts.models import User


class TestMatiereSerializer:
    def test_serialize(self, db):
        matiere = Matiere.objects.create(nom="Mathématiques")
        serializer = MatiereSerializer(matiere)
        assert serializer.data == {"id": matiere.id, "nom": "Mathématiques"}

    def test_deserialize(self, db):
        serializer = MatiereSerializer(data={"nom": "Physique"})
        assert serializer.is_valid()
        matiere = serializer.save()
        assert matiere.nom == "Physique"


class TestProfilEncadreurSerializer:
    def test_serialize_encadreur(self, encadreur_with_matieres):
        serializer = ProfilEncadreurSerializer(encadreur_with_matieres)
        data = serializer.data
        assert data["email"] == "encadreur@test.com"
        assert data["phone"] == "+2250202020202"
        assert data["nom"] == "Encadreur Test"
        assert data["bio"] == "Encadreur expérimenté"
        assert data["tarif_mois"] == 50000
        assert len(data["matieres"]) == 5
        assert data["disponible"] is True
        assert data["verified"] is False

    def test_nom_fallback_to_email(self, db):
        from model_bakery import baker
        user = baker.make(
            User,
            email="onlyemail@test.com",
            phone="+2250303030303",
            first_name="",
            last_name="",
            role=User.Role.ENCADREUR,
        )
        profile = ProfilEncadreur.objects.create(user=user)
        serializer = ProfilEncadreurSerializer(profile)
        assert serializer.data["nom"] == "onlyemail@test.com"

    def test_validate_tarif_mois_negative(self, encadreur_profile):
        data = {"tarif_mois": -100}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert not serializer.is_valid()
        assert "tarif_mois" in serializer.errors

    def test_validate_tarif_horaire_negative(self, encadreur_profile):
        data = {"tarif_horaire": -50}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert not serializer.is_valid()
        assert "tarif_horaire" in serializer.errors

    def test_validate_bio_too_long(self, encadreur_profile):
        data = {"bio": "x" * 2001}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert not serializer.is_valid()
        assert "bio" in serializer.errors

    def test_validate_bio_ok(self, encadreur_profile):
        data = {"bio": "x" * 2000}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert serializer.is_valid()

    def test_validate_cgu_acceptees_false(self, encadreur_profile):
        data = {"cgu_acceptees": False}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert not serializer.is_valid()

    def test_validate_cgu_acceptees_true(self, encadreur_profile):
        data = {"cgu_acceptees": True, "accepte_deplacement": True}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert serializer.is_valid()

    def test_validate_accepte_deplacement_false(self, encadreur_profile):
        data = {"accepte_deplacement": False}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert not serializer.is_valid()

    def test_validate_type_tarif_invalid(self, encadreur_profile):
        data = {"type_tarif": "invalide"}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert not serializer.is_valid()

    def test_update_with_matiere_ids(self, encadreur_profile, matieres):
        matiere_ids = [m.id for m in matieres[:2]]
        data = {"matiere_ids": matiere_ids, "bio": "Nouvelle bio"}
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        encadreur_profile.refresh_from_db()
        assert encadreur_profile.bio == "Nouvelle bio"
        assert encadreur_profile.matieres.count() == 2

    def test_update_sets_questionnaire_rempli(self, encadreur_profile):
        data = {
            "cgu_acceptees": True,
            "accepte_deplacement": True,
            "niveau_etudes": "bac_plus_3",
            "bio": "Test",
        }
        serializer = ProfilEncadreurSerializer(
            encadreur_profile, data=data, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        encadreur_profile.refresh_from_db()
        assert encadreur_profile.questionnaire_rempli is True
