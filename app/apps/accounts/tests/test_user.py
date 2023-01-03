from django.test import TestCase
import factory
from apps.accounts.factories import UserFactory
from apps.accounts.models import User


class TesUserFactory(TestCase):
    """Test create user - UserFactory"""

    def test_create_user(self):
        user = UserFactory(
            email="test@gmail.com",
            password=factory.PostGenerationMethodCall(
                "set_password", "password_default"
            ),
        )

        assert User.objects.filter(email=user.email).exists()
