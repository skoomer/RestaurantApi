import pytest
import factory
from django.test import TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from dj_rest_auth.registration.serializers import RegisterSerializer
from apps.accounts.models import User
from apps.accounts.factories import UserFactory
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
class TestUserView(TestCase):
    """test user profile change password first name"""

    def setUp(self):
        self.data_form = {
            "email": "testgmail@mail.com",
            "password1": "password1245",
            "password2": "password1245",
        }
        self.data_login = {
            "email": "testgmail@mail.com",
            "password": "password1245",
        }
        self.serializer_class = RegisterSerializer
        self.register_url = reverse("rest_register")
        self.profile_url = reverse("rest_user_details")
        self.user = UserFactory(
            email=self.data_form["email"],
            password=factory.PostGenerationMethodCall(
                "set_password", self.data_form["password1"]
            ),
        )
        self.login_url = reverse("rest_login")
        self.user_login = self.client.login(
            username=self.data_login["email"], password=self.data_login["password"]
        )

    def test_profile_get(self):
        assert User.objects.filter(email=self.user.email).exists()

        response = self.user_login
        assert response is True
        response = self.client.get(self.profile_url)
        assert response.status_code == 200
        # get user data  - first name
        assert response.data["first_name"] == "test_first_name"

    def test_profile_update_first_last_name(self):
        data = {"first_name": "change_first_name", "last_name": "change_last_name"}
        response = self.user_login
        assert response is True
        # get user detail - profile
        response = self.client.get(self.profile_url)
        assert response.status_code == 200

        response = self.client.put(
            self.profile_url, data, content_type="application/json"
        )
        assert response.status_code == 200

        # check user with new first name
        assert User.objects.filter(first_name=data["first_name"]).exists()

    def test_user_update_password(self):
        data = {"new_password1": "change_password", "new_password2": "change_password"}
        # check user login
        response = self.user_login
        assert response is True

        # change password
        password_change_url = reverse("rest_password_change")
        response = self.client.post(
            password_change_url, data, content_type="application/json"
        )
        assert response.status_code == 200

        # user logout
        user_logout_url = reverse("rest_logout")
        response = self.client.post(user_logout_url, content_type="application/json")
        assert response.status_code == 200

        # login with new password
        response = self.client.login(
            username=self.data_login["email"], password=data["new_password1"]
        )
        assert response is True

    @pytest.fixture(autouse=True)
    def prepare_fixture(self, file_temp_img):
        self.file_temp_img = file_temp_img

    def test_user_update_avatar(self):
        profile_url = reverse("rest_user_details")
        tmp_file = self.file_temp_img

        with open(tmp_file.name, "rb") as fp:
            response = self.client.put(
                profile_url,
                encode_multipart(BOUNDARY, {"avatar": fp}),
                content_type=MULTIPART_CONTENT,
            )
        assert response.status_code == 200
