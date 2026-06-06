from django.db import models

from backends.accounts.models import User


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = "encadreurs"
        verbose_name = "Matière"
        verbose_name_plural = "Matières"

    def __str__(self):
        return self.nom


class ProfilEncadreur(models.Model):
    TYPE_TARIF_CHOICES = [
        ("mois", "Au mois"),
        ("horaire", "À l'heure"),
        ("les_deux", "Les deux"),
    ]

    NIVEAU_ETUDES_CHOICES = [
        ("bac_en_cours", "BAC en cours"),
        ("bac", "BAC"),
        ("bac_plus_1", "BAC+1"),
        ("bac_plus_2", "BAC+2"),
        ("bac_plus_3", "BAC+3"),
        ("bac_plus_4", "BAC+4"),
        ("bac_plus_5", "BAC+5"),
        ("doctorat", "Doctorat"),
        ("autre", "Autre"),
    ]

    EXPERIENCE_COURS_CHOICES = [
        ("regulier", "Oui, régulièrement"),
        ("occasionnel", "Oui, occasionnellement"),
        ("premiere_fois", "Non, ce sera ma première fois"),
    ]

    NIVEAU_ENSEIGNEMENT_CHOICES = [
        ("primaire", "Primaire"),
        ("college", "Collège"),
        ("lycee", "Lycée"),
        ("superieur", "Supérieur"),
    ]

    JOURS_CHOICES = [
        ("lun", "Lundi"), ("mar", "Mardi"), ("mer", "Mercredi"),
        ("jeu", "Jeudi"), ("ven", "Vendredi"), ("sam", "Samedi"), ("dim", "Dimanche"),
    ]

    CRENEAUX_CHOICES = [
        ("matin", "Matin (8h-12h)"),
        ("apres_midi", "Après-midi (12h-17h)"),
        ("soir", "Soir (17h-20h)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_encadreur")
    bio = models.TextField(blank=True, default="")
    matieres = models.ManyToManyField(Matiere, blank=True, related_name="encadreurs")
    tarif_mois = models.PositiveIntegerField(null=True, blank=True, help_text="Tarif mensuel en FCFA")
    tarif_horaire = models.PositiveIntegerField(null=True, blank=True, help_text="Tarif horaire en FCFA")
    type_tarif = models.CharField(max_length=10, choices=TYPE_TARIF_CHOICES, default="mois")
    disponible = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    note_moyenne = models.FloatField(default=0.0)
    nombre_avis = models.PositiveIntegerField(default=0)
    date_inscription = models.DateTimeField(auto_now_add=True)

    accepte_deplacement = models.BooleanField(default=False)
    niveau_etudes = models.CharField(max_length=20, choices=NIVEAU_ETUDES_CHOICES, blank=True, default="")
    niveaux_enseignement = models.JSONField(default=list, blank=True)
    experience_cours = models.CharField(max_length=20, choices=EXPERIENCE_COURS_CHOICES, blank=True, default="")
    jours_disponibles = models.JSONField(default=list, blank=True)
    creneaux_preferes = models.JSONField(default=list, blank=True)
    autre_matiere = models.CharField(max_length=200, blank=True, default="", help_text="Autre matière (si 'Autre' est sélectionné)")
    cgu_acceptees = models.BooleanField(default=False)
    questionnaire_rempli = models.BooleanField(default=False)

    class Meta:
        app_label = "encadreurs"
        verbose_name = "Profil encadreur"
        verbose_name_plural = "Profils encadreurs"

    def __str__(self):
        return f"Profil de {self.user.email}"
