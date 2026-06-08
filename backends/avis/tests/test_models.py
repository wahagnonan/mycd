import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from backends.avis.models import Avis
from backends.encadreurs.models import ProfilEncadreur


class TestAvisModel:
    def test_create_avis(self, db, parent_user, encadreur_profile):
        avis = Avis.objects.create(
            parent=parent_user,
            encadreur=encadreur_profile,
            note=4,
            commentaire="Bon encadreur",
        )
        assert avis.note == 4
        assert avis.commentaire == "Bon encadreur"
        assert avis.parent == parent_user
        assert avis.encadreur == encadreur_profile
        assert str(avis) == f"Avis de {parent_user.email} - 4/5"

    def test_unique_together(self, db, parent_user, encadreur_profile):
        Avis.objects.create(
            parent=parent_user,
            encadreur=encadreur_profile,
            note=5,
        )
        with pytest.raises(IntegrityError):
            Avis.objects.create(
                parent=parent_user,
                encadreur=encadreur_profile,
                note=3,
            )

    def test_note_validation_min(self, db, parent_user, encadreur_profile):
        avis = Avis(
            parent=parent_user,
            encadreur=encadreur_profile,
            note=0,
        )
        with pytest.raises(ValidationError):
            avis.clean()

    def test_note_validation_max(self, db, parent_user, encadreur_profile):
        avis = Avis(
            parent=parent_user,
            encadreur=encadreur_profile,
            note=6,
        )
        with pytest.raises(ValidationError):
            avis.clean()

    def test_note_boundaries_valid(self, db, parent_user, encadreur_profile):
        avis1 = Avis(parent=parent_user, encadreur=encadreur_profile, note=1)
        avis1.clean()
        avis5 = Avis(
            parent=parent_user,
            encadreur=encadreur_profile,
            note=5,
        )
        avis5.clean()

    def test_ordering(self, db, parent_user, encadreur_profile):
        from backends.accounts.models import User
        from model_bakery import baker
        parent2 = baker.make(User, email="p2@test.com", phone="+2250606060606", role=User.Role.PARENT)
        avis1 = Avis.objects.create(
            parent=parent_user,
            encadreur=encadreur_profile,
            note=4,
        )
        import time
        time.sleep(0.01)
        avis2 = Avis.objects.create(
            parent=parent2,
            encadreur=encadreur_profile,
            note=3,
        )
        qs = Avis.objects.filter(encadreur=encadreur_profile)
        assert list(qs) == [avis2, avis1]


class TestAvisSignals:
    def test_create_updates_encadreur_notes(self, db, parent_user, encadreur_profile):
        Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=4)
        encadreur_profile.refresh_from_db()
        assert encadreur_profile.note_moyenne == 4.0
        assert encadreur_profile.nombre_avis == 1

    def test_multiple_avis_averages(self, db, parent_user, encadreur_profile):
        from backends.accounts.models import User
        from model_bakery import baker

        parent2 = baker.make(User, email="p2@test.com", phone="+2250606060606", role=User.Role.PARENT)

        Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=4)
        Avis.objects.create(parent=parent2, encadreur=encadreur_profile, note=2)
        encadreur_profile.refresh_from_db()
        assert encadreur_profile.note_moyenne == 3.0
        assert encadreur_profile.nombre_avis == 2

    def test_delete_recalculates(self, db, parent_user, encadreur_profile):
        avis = Avis.objects.create(
            parent=parent_user, encadreur=encadreur_profile, note=5
        )
        encadreur_profile.refresh_from_db()
        assert encadreur_profile.nombre_avis == 1
        avis.delete()
        encadreur_profile.refresh_from_db()
        assert encadreur_profile.nombre_avis == 0
        assert encadreur_profile.note_moyenne == 0.0

    def test_avis_creates_notification(self, db, parent_user, encadreur_profile):
        from backends.notifications.models import Notification
        assert Notification.objects.count() == 0
        Avis.objects.create(parent=parent_user, encadreur=encadreur_profile, note=5)
        assert Notification.objects.count() == 1
        notif = Notification.objects.first()
        assert notif.user == encadreur_profile.user
        assert notif.type == Notification.Type.NEW_REVIEW
        assert "5/5" in notif.message
