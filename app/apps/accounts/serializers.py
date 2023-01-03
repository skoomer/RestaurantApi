from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer


class CustomRegisterSerializer(RegisterSerializer):
    username = None


class CustomLoginSerializer(LoginSerializer):
    username = None
