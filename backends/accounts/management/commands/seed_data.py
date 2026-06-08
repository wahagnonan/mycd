from django.core.management.base import BaseCommand

from backends.accounts.models import User
from backends.encadreurs.models import Matiere, ProfilEncadreur


class Command(BaseCommand):
    help = "Crée des comptes de test (encadreurs + parents)"

    def handle(self, *args, **options):
        encadreurs_data = [
            ("Kouassi Konan", "encadreur1@test.com", "+2250700010001", "bac_plus_5",
             "Diplômé en mathématiques avec 5 ans d'expérience",
             ["Mathématiques", "Physique"]),
            ("Diallo Fatou", "encadreur2@test.com", "+2250700010002", "bac_plus_3",
             "Professeur de français certifié, enseigne depuis 2017",
             ["Français"]),
            ("Touré Moussa", "encadreur3@test.com", "+2250700010003", "bac_plus_5",
             "Ingénieur en informatique, enseigne les maths et la programmation",
             ["Mathématiques", "Anglais"]),
        ]
        parents_data = [
            "parent1@test.com", "parent2@test.com", "parent3@test.com",
        ]

        matiere_map = {m.nom: m for m in Matiere.objects.all()}
        phone_base_parent = "+22507000000"

        for nom, email, phone, niveau, bio, matieres in encadreurs_data:
            prenom, nom_famille = nom.split(" ", 1)
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "phone": phone,
                    "role": User.Role.ENCADREUR,
                    "ville": "Abidjan",
                    "quartier": "Cocody",
                    "first_name": prenom,
                    "last_name": nom_famille,
                },
            )
            if created:
                user.set_password("password123")
                user.save()

            profil, _ = ProfilEncadreur.objects.get_or_create(user=user)
            profil.bio = bio
            profil.niveau_etudes = niveau
            profil.niveaux_enseignement = ["college", "lycee"]
            profil.experience_cours = "regulier"
            profil.jours_disponibles = ["lun", "mar", "mer", "jeu", "ven"]
            profil.creneaux_preferes = ["matin", "apres_midi"]
            profil.cgu_acceptees = True
            profil.accepte_deplacement = True
            profil.questionnaire_rempli = True
            profil.tarif_mois = 50000
            profil.tarif_horaire = 5000
            profil.type_tarif = "les_deux"
            profil.disponible = True
            profil.verified = True
            profil.save()
            ids = [matiere_map[m].id for m in matieres if m in matiere_map]
            if ids:
                profil.matieres.set(ids)

            self.stdout.write(f"  Encadreur : {email} ({nom})")

        for i, email in enumerate(parents_data):
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "phone": f"{phone_base_parent}{i + 1:02d}",
                    "role": User.Role.PARENT,
                    "ville": "Abidjan",
                    "quartier": "Cocody",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            self.stdout.write(f"  Parent : {email}")

        self.stdout.write(self.style.SUCCESS("Comptes de test créés avec succès"))
        self.stdout.write("Mot de passe pour tous : password123")
