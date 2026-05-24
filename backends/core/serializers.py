from django.db import IntegrityError
from rest_framework import serializers

from .models import Avis, Conversation, Matiere, Message, Notification, ProfilEncadreur, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("email", "phone", "password", "password2", "role", "ville", "quartier")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError as e:
            if "email" in str(e):
                raise serializers.ValidationError({"email": "Cet email est déjà utilisé"})
            if "phone" in str(e):
                raise serializers.ValidationError({"phone": "Ce téléphone est déjà utilisé"})
            raise


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "role", "ville", "quartier")
        read_only_fields = ("id",)


class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ("id", "nom")


class ProfilEncadreurSerializer(serializers.ModelSerializer):
    matieres = MatiereSerializer(many=True, read_only=True)
    matiere_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    ville = serializers.CharField(source="user.ville", read_only=True)
    quartier = serializers.CharField(source="user.quartier", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    nom = serializers.SerializerMethodField()

    # Champs du questionnaire — en écriture seule pour la soumission initiale
    cgu_acceptees = serializers.BooleanField(write_only=True, required=False)
    accepte_deplacement = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = ProfilEncadreur
        fields = (
            "id", "user_id", "email", "phone", "nom", "bio", "ville", "quartier",
            "matieres", "matiere_ids",
            "tarif_mois", "tarif_horaire", "type_tarif",
            "disponible", "verified", "note_moyenne", "date_inscription",
            "accepte_deplacement", "niveau_etudes", "niveaux_enseignement",
            "experience_cours", "jours_disponibles", "creneaux_preferes",
            "cgu_acceptees", "questionnaire_rempli",
        )
        read_only_fields = (
            "id", "verified", "note_moyenne", "date_inscription",
            "questionnaire_rempli",
        )

    def get_nom(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email

    def validate_tarif_mois(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Le tarif mensuel ne peut pas être négatif")
        return value

    def validate_tarif_horaire(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Le tarif horaire ne peut pas être négatif")
        return value

    def validate_type_tarif(self, value):
        if value not in dict(ProfilEncadreur.TYPE_TARIF_CHOICES):
            raise serializers.ValidationError(f"Type de tarif invalide : {value}")
        return value

    def validate_bio(self, value):
        if value and len(value) > 2000:
            raise serializers.ValidationError("La bio ne peut pas dépasser 2000 caractères")
        return value

    def validate_cgu_acceptees(self, value):
        if value is True:
            return value
        raise serializers.ValidationError("Vous devez accepter les conditions générales d'utilisation")

    def validate_accepte_deplacement(self, value):
        if value is True:
            return value
        raise serializers.ValidationError("Vous devez accepter de vous déplacer au domicile de l'élève")

    def update(self, instance, validated_data):
        matiere_ids = validated_data.pop("matiere_ids", None)

        # Détecter la soumission du questionnaire pour basculer questionnaire_rempli
        questionnaire_fields = {"niveau_etudes", "niveaux_enseignement", "experience_cours",
                                "jours_disponibles", "cgu_acceptees", "accepte_deplacement"}
        if questionnaire_fields & set(validated_data.keys()):
            instance.questionnaire_rempli = True

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if matiere_ids is not None:
            instance.matieres.set(Matiere.objects.filter(id__in=matiere_ids))
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    sender_nom = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "sender", "sender_email", "sender_nom", "content",
                  "created_at", "is_read")
        read_only_fields = ("id", "sender", "created_at", "is_read")

    def get_sender_nom(self, obj):
        nom = f"{obj.sender.first_name} {obj.sender.last_name}".strip()
        return nom or obj.sender.email


class ConversationListSerializer(serializers.ModelSerializer):
    dernier_message = serializers.SerializerMethodField()
    nb_non_lus = serializers.SerializerMethodField()
    correspondant_nom = serializers.SerializerMethodField()
    correspondant_email = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "correspondant_nom", "correspondant_email",
                  "dernier_message", "nb_non_lus", "updated_at")

    def get_correspondant(self, obj, user):
        return obj.encadreur if user == obj.parent else obj.parent

    def get_correspondant_nom(self, obj):
        user = self.context["request"].user
        c = self.get_correspondant(obj, user)
        nom = f"{c.first_name} {c.last_name}".strip()
        return nom or c.email

    def get_correspondant_email(self, obj):
        user = self.context["request"].user
        return self.get_correspondant(obj, user).email

    def get_dernier_message(self, obj):
        msg = obj.messages.last()
        if not msg:
            return None
        return {
            "content": msg.content[:80],
            "created_at": msg.created_at.isoformat(),
            "est_moi": msg.sender == self.context["request"].user,
        }

    def get_nb_non_lus(self, obj):
        return obj.messages.filter(is_read=False).exclude(
            sender=self.context["request"].user
        ).count()


class CreateConversationSerializer(serializers.Serializer):
    encadreur_id = serializers.IntegerField()

    def validate_encadreur_id(self, value):
        user = self.context["request"].user
        if user.role != User.Role.PARENT:
            raise serializers.ValidationError("Seuls les parents peuvent initier une conversation")
        try:
            encadreur = User.objects.get(id=value, role=User.Role.ENCADREUR)
        except User.DoesNotExist:
            raise serializers.ValidationError("Encadreur introuvable")
        if encadreur == user:
            raise serializers.ValidationError("Vous ne pouvez pas vous contacter vous-même")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "type", "title", "message", "link", "is_read", "created_at")
        read_only_fields = ("id", "type", "title", "message", "link", "created_at")


class AvisSerializer(serializers.ModelSerializer):
    parent_nom = serializers.SerializerMethodField()
    parent_email = serializers.EmailField(source="parent.email", read_only=True)

    class Meta:
        model = Avis
        fields = ("id", "parent", "parent_nom", "parent_email", "note", "commentaire", "created_at")
        read_only_fields = ("id", "parent", "created_at")

    def get_parent_nom(self, obj):
        nom = f"{obj.parent.first_name} {obj.parent.last_name}".strip()
        return nom or obj.parent.email

    def validate_note(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être comprise entre 1 et 5")
        return value