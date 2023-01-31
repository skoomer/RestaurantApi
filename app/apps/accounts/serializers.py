from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from apps.accounts.models import User


class CustomRegisterSerializer(RegisterSerializer):
    username = None


class CustomLoginSerializer(LoginSerializer):
    username = None


class UserSerializer(UserDetailsSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "avatar")
        extra_kwargs = {
            "email": {"read_only": True},
        }
