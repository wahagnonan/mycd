import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from backends.accounts.models import User
from backends.encadreurs.models import Matiere, ProfilEncadreur


def _seed_users(kind: str, count: int, role: str) -> list[User]:
    users = []
    phone_base = {"parent": "+22507000000", "encadreur": "+22507000100"}
    base_phone = phone_base[role]

    for i in range(1, count + 1):
        email = f"{kind}{i}@test.com"
        phone = f"{base_phone}{i:02d}"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "phone": phone,
                "role": role,
                "ville": "Abidjan",
                "quartier": "Cocody",
                "first_name": kind.capitalize(),
                "last_name": str(i),
                "is_active": True,
            },
        )
        if created:
            user.set_password("password123")
            user.save()
        users.append(user)
    return users


class Command(BaseCommand):
    help = "Crée 10 encadreurs et 10 parents (photos uniquement pour les encadreurs)"

    def handle(self, *args, **options):
        images_dir = Path.home() / "Téléchargements"

        if not images_dir.exists():
            self.stderr.write(f"Répertoire introuvable : {images_dir}")
            return

        # Nettoyer les anciennes données
        User.objects.filter(email__regex=r"^(encadreur|parent)\d+@test\.com$").delete()
        self.stdout.write("Anciennes données nettoyées")

        encadreurs = _seed_users("encadreur", 10, User.Role.ENCADREUR)
        parents = _seed_users("parent", 10, User.Role.PARENT)

        encadreur_images = {
            1: "ed1.jpeg", 2: "ed2.jpeg", 3: "ed3.jpeg", 4: "ed4.jpeg",
            5: "ed5.jpeg", 6: "ed6.jpeg", 7: "ed7.jpeg",
        }
        photos_dir = Path(settings.MEDIA_ROOT) / "encadreurs"
        photos_dir.mkdir(parents=True, exist_ok=True)

        matieres = list(Matiere.objects.all())
        noms_encadreurs = [
            "Kouassi Konan", "Diallo Fatou", "Touré Moussa", "Bamba Aminata",
            "Koné Adama", "Ouattara Rachel", "Cissé Ibrahim", "Soro Fatoumata",
            "Traoré Issa", "Tano Awa",
        ]
        bios = [
            "Diplômé en mathématiques avec 5 ans d'expérience",
            "Professeur de français certifié, enseigne depuis 2017",
            "Expert en physique-chimie, ancien élève de l'ENS",
            "Anglais natif, prépare aux examens internationaux",
            "Bac+5 en sciences, pédagogie adaptée à chaque élève",
            "10 ans d'expérience dans l'enseignement secondaire",
            "Ingénieur en informatique, enseigne les maths et la programmation",
            "Doctorante en lettres, passionnée de transmission",
            "Ancien enseignant en lycée, spécialiste des SVT",
            "Pédagogue expérimentée, cours du primaire au supérieur",
        ]
        niveaux = [
            "bac_plus_5", "bac_plus_3", "bac_plus_5", "bac_plus_3",
            "bac_plus_5", "bac_plus_2", "bac_plus_5", "bac_plus_5",
            "bac_plus_3", "bac_plus_5",
        ]

        for i, enc in enumerate(encadreurs):
            profil, _ = ProfilEncadreur.objects.get_or_create(user=enc)
            profil.bio = bios[i]
            profil.niveau_etudes = niveaux[i]
            profil.niveaux_enseignement = ["college", "lycee"]
            profil.experience_cours = "regulier"
            profil.jours_disponibles = ["lun", "mar", "mer", "jeu", "ven"]
            profil.creneaux_preferes = ["matin", "apres_midi"]
            profil.cgu_acceptees = True
            profil.accepte_deplacement = True
            profil.questionnaire_rempli = True
            profil.tarif_mois = 50000 + i * 5000
            profil.tarif_horaire = 5000 + i * 500
            profil.type_tarif = "les_deux"
            profil.verified = i < 5
            if matieres:
                profil.matieres.set([matieres[i % len(matieres)]])

            # Photo encadreur
            img_name = encadreur_images.get(i + 1)
            if img_name:
                src = images_dir / img_name
                if src.exists():
                    dst = photos_dir / f"encadreur_{i + 1}{src.suffix}"
                    shutil.copy2(src, dst)
                    with open(dst, "rb") as f:
                        profil.photo.save(f"encadreur_{i + 1}{src.suffix}", File(f), save=False)

            profil.save()

            # Mettre à jour le nom complet
            prenom, nom = noms_encadreurs[i].split(" ", 1)
            enc.first_name = prenom
            enc.last_name = nom
            enc.save()

        self.stdout.write(self.style.SUCCESS(f"Créés : {len(encadreurs)} encadreurs, {len(parents)} parents"))
