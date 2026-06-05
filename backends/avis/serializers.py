from rest_framework import serializers

from backends.avis.models import Avis


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
