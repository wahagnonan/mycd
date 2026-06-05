from django.db import IntegrityError
from rest_framework import serializers

from backends.accounts.models import User


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
