from rest_framework import serializers

from backends.accounts.models import User
from backends.messagerie.models import Conversation, Message


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
