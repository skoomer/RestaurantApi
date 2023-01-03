import pytest
from django.test import TestCase, Client
from dj_rest_auth.registration.app_settings import RegisterSerializer
from apps.accounts.models import User
from django.urls import reverse
from django.core import mail


@pytest.mark.django_db(transaction=True)
class TestUserView(TestCase):
    """user views"""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.serializer_class = RegisterSerializer
        self.register_url = reverse("rest_register")
        self.login_url = reverse("rest_login")
        self.data_form = {
            "email": "testgmail@mail.com",
            "password1": "password1245",
            "password2": "password1245",
        }
        self.data_login = {
            "email": "testgmail@mail.com",
            "password": "password1245",
        }

    def test_create_user(self):
        """test create user"""

        serializer = self.serializer_class(data=self.data_form)
        assert serializer.is_valid() is True

        response = self.client.post(self.register_url, self.data_form)
        assert response.status_code == 201

        user = User.objects.filter(email="testgmail@mail.com").exists()
        assert user is True

    def test_login_no_verify_email(self):
        responses = self.client.post(self.login_url, self.data_login)

        assert responses.status_code == 400
        self.assertEqual(
            responses.json()["non_field_errors"],
            ["Unable to log in with provided credentials."],
        )

    def test_user_login_with_confirm_email(self):

        # create user
        responses = self.client.post(self.register_url, self.data_form)
        assert responses.status_code == 201
        self.assertEqual(responses.json()["detail"], "Verification e-mail sent.")

        # send verify email
        url = reverse("rest_resend_email")
        responses = self.client.post(url, {"email": "testgmail@mail.com"})
        assert responses.status_code == 200

        # parse email
        self.assertEqual(len(mail.outbox), 1)
        email_lines = mail.outbox[0].body.splitlines()
        activation_line = [lines for lines in email_lines if "account-confirm-email" in lines][0]
        activation_link = activation_line.split("go to ")[1]
        activation_key = activation_link.split("/")[6]

        # verify email
        url = reverse("rest_verify_email")
        response = self.client.post(url, {"key": activation_key})
        assert response.status_code == 200

        # login
        responses = self.client.post(self.login_url, self.data_login)
        assert responses.status_code == 200
