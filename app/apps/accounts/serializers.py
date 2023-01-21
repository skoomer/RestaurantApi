from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer

# pylint: disable=W0223


class CustomRegisterSerializer(RegisterSerializer):
    """override RegisterSerializer for custom registration"""

    username = None


class CustomLoginSerializer(LoginSerializer):
    """override LoginSerializer for custom sign in"""

    username = None
