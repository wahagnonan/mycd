import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from backends.accounts.models import User, UserManager, phone_validator


class TestUserManager:
    def test_create_user(self, db):
        user = User.objects.create_user(
            email="test@example.com",
            password="secret123",
            phone="+2250101010101",
            role=User.Role.PARENT,
        )
        assert user.email == "test@example.com"
        assert user.check_password("secret123")
        assert user.phone == "+2250101010101"
        assert user.role == User.Role.PARENT
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_without_email(self, db):
        with pytest.raises(ValueError, match="email est obligatoire"):
            User.objects.create_user(email="", password="secret123")

    def test_create_superuser(self, db):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            phone="+2250202020202",
        )
        assert user.is_staff
        assert user.is_superuser

    def test_create_superuser_must_be_staff(self, db):
        with pytest.raises(ValueError, match="must have is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="admin123",
                phone="+2250202020202",
                is_staff=False,
            )

    def test_create_superuser_must_be_superuser(self, db):
        with pytest.raises(ValueError, match="must have is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="admin123",
                phone="+2250202020202",
                is_superuser=False,
            )


class TestUserModel:
    def test_str(self, db):
        user = User.objects.create_user(
            email="test@example.com",
            password="secret123",
            phone="+2250101010101",
            role=User.Role.PARENT,
        )
        assert str(user) == "test@example.com (parent)"

    def test_email_unique(self, db):
        User.objects.create_user(
            email="same@example.com",
            password="secret123",
            phone="+2250101010101",
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="same@example.com",
                password="secret456",
                phone="+2250202020202",
            )

    def test_phone_unique(self, db):
        User.objects.create_user(
            email="one@example.com",
            password="secret123",
            phone="+2250101010101",
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="two@example.com",
                password="secret456",
                phone="+2250101010101",
            )

    def test_default_role_is_parent(self, db):
        user = User.objects.create_user(
            email="parent@example.com",
            password="secret123",
            phone="+2250101010101",
        )
        assert user.role == User.Role.PARENT

    def test_username_is_none(self, db):
        user = User.objects.create_user(
            email="test@example.com",
            password="secret123",
            phone="+2250101010101",
        )
        assert user.username is None


class TestPhoneValidator:
    def test_valid_phone(self):
        phone_validator("+2250101010101")

    def test_invalid_phone_missing_prefix(self):
        with pytest.raises(ValidationError):
            phone_validator("0101010101")

    def test_invalid_phone_wrong_prefix(self):
        with pytest.raises(ValidationError):
            phone_validator("+33601010101")

    def test_invalid_phone_too_short(self):
        with pytest.raises(ValidationError):
            phone_validator("+22501010101")

    def test_invalid_phone_too_long(self):
        with pytest.raises(ValidationError):
            phone_validator("+22501010101010")
