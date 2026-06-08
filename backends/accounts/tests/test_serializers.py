import pytest
from django.db import IntegrityError

from backends.accounts.models import User
from backends.accounts.serializers import RegisterSerializer, LoginSerializer, UserSerializer


class TestRegisterSerializer:
    def test_valid_registration(self, db):
        data = {
            "email": "new@test.com",
            "phone": "+2250101010101",
            "password": "secret123",
            "password2": "secret123",
            "role": User.Role.PARENT,
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_password_mismatch(self, db):
        data = {
            "email": "new@test.com",
            "phone": "+2250101010101",
            "password": "secret123",
            "password2": "different",
            "role": User.Role.PARENT,
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "Les mots de passe ne correspondent pas" in str(serializer.errors)

    def test_password_too_short(self, db):
        data = {
            "email": "new@test.com",
            "phone": "+2250101010101",
            "password": "12",
            "password2": "12",
            "role": User.Role.PARENT,
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_duplicate_email(self, db):
        User.objects.create_user(
            email="existing@test.com",
            password="secret123",
            phone="+2250101010101",
        )
        data = {
            "email": "existing@test.com",
            "phone": "+2250202020202",
            "password": "secret123",
            "password2": "secret123",
            "role": User.Role.PARENT,
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_duplicate_phone(self, db):
        User.objects.create_user(
            email="existing@test.com",
            password="secret123",
            phone="+2250101010101",
        )
        data = {
            "email": "new@test.com",
            "phone": "+2250101010101",
            "password": "secret123",
            "password2": "secret123",
            "role": User.Role.PARENT,
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()


class TestLoginSerializer:
    def test_valid(self):
        serializer = LoginSerializer(data={
            "email": "test@test.com",
            "password": "secret123",
        })
        assert serializer.is_valid()

    def test_missing_email(self):
        serializer = LoginSerializer(data={"password": "secret123"})
        assert not serializer.is_valid()

    def test_missing_password(self):
        serializer = LoginSerializer(data={"email": "test@test.com"})
        assert not serializer.is_valid()


class TestUserSerializer:
    def test_serialization(self, db):
        user = User.objects.create_user(
            email="test@test.com",
            password="secret123",
            phone="+2250101010101",
            role=User.Role.PARENT,
            ville="Abidjan",
            quartier="Cocody",
        )
        serializer = UserSerializer(user)
        assert serializer.data["email"] == "test@test.com"
        assert serializer.data["phone"] == "+2250101010101"
        assert serializer.data["role"] == "parent"
        assert serializer.data["ville"] == "Abidjan"
        assert serializer.data["quartier"] == "Cocody"
        assert "password" not in serializer.data

    def test_read_only_fields(self):
        serializer = UserSerializer()
        assert "id" in serializer.Meta.read_only_fields
