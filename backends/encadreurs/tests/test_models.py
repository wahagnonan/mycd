import pytest
from django.db import IntegrityError

from backends.encadreurs.models import Matiere, ProfilEncadreur
from backends.accounts.models import User


class TestMatiereModel:
    def test_create_matiere(self, db):
        matiere = Matiere.objects.create(nom="Mathématiques")
        assert matiere.nom == "Mathématiques"
        assert str(matiere) == "Mathématiques"

    def test_matiere_unique(self, db):
        Matiere.objects.create(nom="Français")
        with pytest.raises(IntegrityError):
            Matiere.objects.create(nom="Français")


class TestProfilEncadreurModel:
    def test_create_profile(self, encadreur_user):
        profile = ProfilEncadreur.objects.create(user=encadreur_user)
        assert profile.user == encadreur_user
        assert profile.disponible is True
        assert profile.verified is False
        assert profile.note_moyenne == 0.0
        assert profile.nombre_avis == 0
        assert str(profile) == f"Profil de {encadreur_user.email}"

    def test_profile_one_to_one(self, encadreur_user):
        ProfilEncadreur.objects.create(user=encadreur_user)
        with pytest.raises(IntegrityError):
            ProfilEncadreur.objects.create(user=encadreur_user)

    def test_default_field_values(self, encadreur_user):
        profile = ProfilEncadreur.objects.create(user=encadreur_user)
        assert profile.bio == ""
        assert profile.tarif_mois is None
        assert profile.tarif_horaire is None
        assert profile.type_tarif == "mois"
        assert profile.niveau_etudes == ""
        assert profile.niveaux_enseignement == []
        assert profile.jours_disponibles == []
        assert profile.creneaux_preferes == []
        assert profile.autre_matiere == ""
        assert profile.cgu_acceptees is False
        assert profile.questionnaire_rempli is False

    def test_matieres_many_to_many(self, encadreur_profile, matieres):
        encadreur_profile.matieres.set(matieres)
        assert encadreur_profile.matieres.count() == 5
        assert list(encadreur_profile.matieres.all().order_by("nom")) == sorted(
            matieres, key=lambda m: m.nom
        )

    def test_profile_cascades_on_user_delete(self, encadreur_user, db):
        profile = ProfilEncadreur.objects.create(user=encadreur_user)
        user_id = encadreur_user.id
        encadreur_user.delete()
        assert ProfilEncadreur.objects.filter(id=profile.id).count() == 0
