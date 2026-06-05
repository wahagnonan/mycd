from rest_framework import serializers

from backends.paiement.models import CreditAchat, CreditUtilisation, Paiement


class PaiementSerializer(serializers.ModelSerializer):
    encadreur_nom = serializers.SerializerMethodField()
    parent_nom = serializers.SerializerMethodField()

    class Meta:
        model = Paiement
        fields = (
            "id", "parent", "parent_nom", "encadreur", "encadreur_nom",
            "montant", "type", "statut", "token_paydunya", "receipt_url",
            "description", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "parent", "statut", "token_paydunya", "receipt_url",
            "created_at", "updated_at",
        )

    def get_parent_nom(self, obj):
        nom = f"{obj.parent.first_name} {obj.parent.last_name}".strip()
        return nom or obj.parent.email

    def get_encadreur_nom(self, obj):
        nom = f"{obj.encadreur.user.first_name} {obj.encadreur.user.last_name}".strip()
        return nom or obj.encadreur.user.email


class InitierPaiementSerializer(serializers.Serializer):
    montant = serializers.IntegerField(min_value=100)
    type = serializers.ChoiceField(choices=Paiement.TypePaiement.choices)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_montant(self, value):
        if value > 1000000:
            raise serializers.ValidationError("Le montant ne peut pas dépasser 1 000 000 FCFA")
        return value


class CreditAchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditAchat
        fields = ("id", "parent", "credits_achetes", "montant", "token_paydunya", "receipt_url", "statut", "created_at")
        read_only_fields = ("id", "parent", "token_paydunya", "receipt_url", "statut", "created_at")


class CreditUtilisationSerializer(serializers.ModelSerializer):
    encadreur_nom = serializers.SerializerMethodField()
    encadreur_email = serializers.EmailField(source="encadreur.user.email", read_only=True)

    class Meta:
        model = CreditUtilisation
        fields = ("id", "encadreur", "encadreur_nom", "encadreur_email", "created_at")
        read_only_fields = ("id", "created_at")

    def get_encadreur_nom(self, obj):
        nom = f"{obj.encadreur.user.first_name} {obj.encadreur.user.last_name}".strip()
        return nom or obj.encadreur.user.email
