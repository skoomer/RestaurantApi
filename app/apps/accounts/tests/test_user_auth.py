import pytest
from django.test import TestCase
from dj_rest_auth.registration.app_settings import RegisterSerializer
from apps.accounts.models import User
from rest_framework import status
from django.urls import reverse
from django.core import mail


@pytest.mark.django_db(transaction=True)
class TestUserView(TestCase):
    """user views"""

    register_url = reverse("rest_register")
    login_url = reverse("rest_login")

    def setUp(self):
        self.serializer_class = RegisterSerializer

        self.data_form = {
            "email": "testgmail@mail.com",
            "password1": "password1245",
            "password2": "password1245",
        }
        self.data_login = {
            "email": "testgmail@mail.com",
            "password": "password1245",
        }

    def activations_key(self):
        # parse email
        email_lines = mail.outbox[0].body.splitlines()
        activation_line = [
            lines for lines in email_lines if "account-confirm-email" in lines
        ][0]
        activation_link = activation_line.split("go to ")[1]
        activation_key = activation_link.split("/")[6]
        return activation_key

    @pytest.mark.django_db(transaction=True)
    def test_create_user(self):
        """test create user"""

        serializer = self.serializer_class(data=self.data_form)
        assert serializer.is_valid() is True

        response = self.client.post(self.register_url, self.data_form)
        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.filter(email="testgmail@mail.com").exists()
        assert user is True

    def test_login_no_verify_email(self):
        responses = self.client.post(self.login_url, self.data_login)

        assert responses.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Unable to log in with provided credentials."
            in responses.data["non_field_errors"]
        )

    def test_user_login_with_confirm_email(self):

        # create user
        responses = self.client.post(self.register_url, self.data_form)
        assert responses.status_code == status.HTTP_201_CREATED
        self.assertEqual(responses.json()["detail"], "Verification e-mail sent.")

        # send verify email
        url = reverse("rest_resend_email")
        responses = self.client.post(url, {"email": "testgmail@mail.com"})
        assert responses.status_code == status.HTTP_200_OK

        # verify email
        url = reverse("rest_verify_email")
        response = self.client.post(url, {"key": self.activations_key()})
        assert response.status_code == status.HTTP_200_OK

    def test_login_user_with_confirm_email(self):
        # create user
        responses = self.client.post(self.register_url, self.data_form)
        assert responses.status_code == status.HTTP_201_CREATED
        self.assertEqual(responses.json()["detail"], "Verification e-mail sent.")

        # send verify email
        url = reverse("rest_resend_email")
        responses = self.client.post(url, {"email": "testgmail@mail.com"})
        assert responses.status_code == status.HTTP_200_OK

        # verify email
        url = reverse("rest_verify_email")
        response = self.client.post(url, {"key": self.activations_key()})
        assert response.status_code == status.HTTP_200_OK
        # login
        response = self.client.post(self.login_url, self.data_login)
        assert response.status_code == status.HTTP_200_OK
