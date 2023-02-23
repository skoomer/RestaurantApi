from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from apps.accounts.models import User

# pylint: disable=W0223


class CustomRegisterSerializer(RegisterSerializer):
    """override RegisterSerializer for custom registration"""

    username = None


class CustomLoginSerializer(LoginSerializer):
    """override LoginSerializer for custom sign in"""

    username = None


class UserSerializer(UserDetailsSerializer):
    """User serializer"""
    class Meta:
        """change email on  readonly option"""
        model = User
        fields = ("email", "first_name", "last_name", "avatar")
        extra_kwargs = {
            "email": {"read_only": True},
        }
