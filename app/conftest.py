import pytest
from django.test.client import Client

# pylint: disable=W0621


@pytest.fixture()
def client():

    client = Client(enforce_csrf_checks=False)
    return client
