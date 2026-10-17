import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


@pytest.fixture
def client():
    application = create_app(Settings(_env_file=None))
    with TestClient(application) as test_client:
        yield test_client
