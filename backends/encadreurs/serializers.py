from rest_framework import serializers

from backends.accounts.models import User
from backends.encadreurs.models import Matiere, ProfilEncadreur
from backends.paiement.helpers import a_debloque_encadreur


class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ("id", "nom")


class ProfilEncadreurPublicSerializer(serializers.ModelSerializer):
    matieres = MatiereSerializer(many=True, read_only=True)
    ville = serializers.CharField(source="user.ville", read_only=True)
    quartier = serializers.CharField(source="user.quartier", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    nom = serializers.SerializerMethodField()
    debloque = serializers.SerializerMethodField()

    class Meta:
        model = ProfilEncadreur
        fields = (
            "id", "user_id", "nom", "bio", "ville", "quartier",
            "matieres",
            "tarif_mois", "tarif_horaire", "type_tarif",
            "disponible", "verified", "note_moyenne", "nombre_avis", "date_inscription",
            "autre_matiere", "debloque",
        )
        read_only_fields = (
            "id", "verified", "note_moyenne", "date_inscription",
        )

    def get_nom(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or "Encadreur"

    def get_debloque(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == User.Role.PARENT:
            debloque_ids = self.context.get("debloque_ids")
            if debloque_ids is not None:
                return obj.id in debloque_ids
            return a_debloque_encadreur(request.user, obj)
        return False


class ProfilEncadreurSerializer(ProfilEncadreurPublicSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    matiere_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    cgu_acceptees = serializers.BooleanField(write_only=True, required=False)
    accepte_deplacement = serializers.BooleanField(write_only=True, required=False)

    class Meta(ProfilEncadreurPublicSerializer.Meta):
        fields = (
            "id", "user_id", "email", "phone", "nom", "bio", "ville", "quartier",
            "matieres", "matiere_ids",
            "tarif_mois", "tarif_horaire", "type_tarif",
            "disponible", "verified", "note_moyenne", "nombre_avis", "date_inscription",
            "accepte_deplacement", "niveau_etudes", "niveaux_enseignement",
            "experience_cours", "jours_disponibles", "creneaux_preferes",
            "cgu_acceptees", "questionnaire_rempli", "autre_matiere",
            "debloque",
        )
        read_only_fields = (
            "id", "verified", "note_moyenne", "date_inscription",
            "questionnaire_rempli",
        )

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
