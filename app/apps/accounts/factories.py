import factory
from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    """User factory"""

    class Meta:
        """meta user"""

        model = User

    first_name = "test_first_name"
    last_name = "test_last_name"
    is_admin = False
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")
    email = factory.LazyAttribute(lambda o: "%s@example.org" % o.first_name)
