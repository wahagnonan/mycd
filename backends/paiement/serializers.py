from rest_framework import serializers

from backends.paiement.models import CreditAchat, CreditUtilisation


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
