from tempfile import NamedTemporaryFile
import pytest
from django.test.client import Client
from PIL import Image


@pytest.fixture(scope="class", autouse=True)
def client():
    return Client(enforce_csrf_checks=False)


@pytest.fixture(scope="function")
def file_temp_img():
    image = Image.new("RGB", (100, 100))
    tmp_file = NamedTemporaryFile(suffix=".jpg")
    image.save(tmp_file)
    tmp_file.seek(0)
    return tmp_file
