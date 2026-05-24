from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+225\d{10}$",
    message="Le numéro doit être au format +225XXXXXXXXXX",
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        PARENT = "parent", "Parent"
        ENCADREUR = "encadreur", "Encadreur"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARENT)
    phone = models.CharField(max_length=20, unique=True, validators=[phone_validator])
    ville = models.CharField(max_length=100, blank=True, default="")
    quartier = models.CharField(max_length=100, blank=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    objects = UserManager()

    class Meta:
        app_label = "core"

    def __str__(self):
        return f"{self.email} ({self.role})"


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = "core"
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

    # Questionnaire post-inscription
    accepte_deplacement = models.BooleanField(default=False)
    niveau_etudes = models.CharField(max_length=20, choices=NIVEAU_ETUDES_CHOICES, blank=True, default="")
    niveaux_enseignement = models.JSONField(default=list, blank=True)
    experience_cours = models.CharField(max_length=20, choices=EXPERIENCE_COURS_CHOICES, blank=True, default="")
    jours_disponibles = models.JSONField(default=list, blank=True)
    creneaux_preferes = models.JSONField(default=list, blank=True)
    cgu_acceptees = models.BooleanField(default=False)
    questionnaire_rempli = models.BooleanField(default=False)

    class Meta:
        app_label = "core"
        verbose_name = "Profil encadreur"
        verbose_name_plural = "Profils encadreurs"

    def __str__(self):
        return f"Profil de {self.user.email}"


class Conversation(models.Model):
    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_as_parent"
    )
    encadreur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_as_encadreur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        unique_together = ("parent", "encadreur")
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Conversation {self.parent.email} ↔ {self.encadreur.email}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        app_label = "core"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ("created_at",)

    def __str__(self):
        return f"Message de {self.sender.email} à {self.created_at:%d/%m %H:%M}"


class Notification(models.Model):
    class Type(models.TextChoices):
        NEW_MESSAGE = "new_message", "Nouveau message"
        PROFILE_VERIFIED = "profile_verified", "Profil vérifié"
        NEW_REVIEW = "new_review", "Nouvel avis"
        PAYMENT_RECEIVED = "payment_received", "Paiement reçu"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, default="")
    link = models.CharField(max_length=500, blank=True, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ("-created_at",)

    def __str__(self):
        return f"[{'Lu' if self.is_read else 'Non lu'}] {self.title}"


class Avis(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avis_donnes")
    encadreur = models.ForeignKey(
        ProfilEncadreur, on_delete=models.CASCADE, related_name="avis_recus"
    )
    note = models.PositiveSmallIntegerField(help_text="Note de 1 à 5")
    commentaire = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ("parent", "encadreur")
        ordering = ("-created_at",)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.note < 1 or self.note > 5:
            raise ValidationError({"note": "La note doit être comprise entre 1 et 5."})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.clean()
        super().save(*args, **kwargs)
        if is_new:
            Notification.objects.create(
                user=self.encadreur.user,
                type=Notification.Type.NEW_REVIEW,
                title=f"Nouvel avis de {self.parent.email}",
                message=f"Note : {self.note}/5" + (f" — {self.commentaire[:100]}" if self.commentaire else ""),
                link=f"/encadreurs/{self.encadreur.id}",
            )

    def __str__(self):
        return f"Avis de {self.parent.email} - {self.note}/5"


class Paiement(models.Model):
    class TypePaiement(models.TextChoices):
        COURS_MOIS = "cours_mois", "Cours au mois"
        COURS_HORAIRE = "cours_horaire", "Cours à l'heure"

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        COMPLETE = "complete", "Complété"
        ECHOUE = "echoue", "Échoué"
        REMBOURSE = "rembourse", "Remboursé"

    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="paiements_emis"
    )
    encadreur = models.ForeignKey(
        ProfilEncadreur, on_delete=models.CASCADE, related_name="paiements_recus"
    )
    montant = models.PositiveIntegerField(help_text="Montant en FCFA")
    type = models.CharField(
        max_length=20, choices=TypePaiement.choices, default=TypePaiement.COURS_MOIS
    )
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    token_paydunya = models.CharField(max_length=100, blank=True, default="")
    receipt_url = models.URLField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Paiement {self.id} — {self.montant} FCFA ({self.statut})"


class CreditAchat(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        COMPLETE = "complete", "Complété"
        ECHOUE = "echoue", "Échoué"

    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credit_achats")
    credits_achetes = models.PositiveIntegerField(default=3)
    montant = models.PositiveIntegerField(help_text="Montant payé en FCFA")
    token_paydunya = models.CharField(max_length=100, blank=True, default="")
    receipt_url = models.URLField(blank=True, default="")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        ordering = ("-created_at",)
        verbose_name = "Achat de crédits"
        verbose_name_plural = "Achats de crédits"

    def __str__(self):
        return f"CreditAchat {self.id} — {self.parent.email} ({self.credits_achetes} crédits, {self.statut})"


class CreditUtilisation(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credits_utilises")
    encadreur = models.ForeignKey(
        ProfilEncadreur, on_delete=models.CASCADE, related_name="credits_consommes"
    )
    credit_achat = models.ForeignKey(
        CreditAchat, on_delete=models.SET_NULL, null=True, blank=True, related_name="utilisations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        unique_together = ("parent", "encadreur")
        verbose_name = "Utilisation de crédit"
        verbose_name_plural = "Utilisations de crédits"

    def __str__(self):
        return f"Crédit utilisé: {self.parent.email} → {self.encadreur.user.email}"
