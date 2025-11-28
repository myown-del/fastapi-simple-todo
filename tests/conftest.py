import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise

from app.main import app
from app.core.db import TortoiseSettings


@pytest.fixture(scope="function")
async def test_db():
    tortoise_settings = TortoiseSettings.generate(test_db=True)
    
    await Tortoise.init(
        db_url=tortoise_settings.db_url,
        modules=tortoise_settings.modules
    )
    await Tortoise.generate_schemas()
    
    yield
    
    await Tortoise.close_connections()


@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_credentials():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def registered_user(client, test_user_credentials):
    user_data = {
        "email": test_user_credentials["email"],
        "password": test_user_credentials["password"],
        "first_name": test_user_credentials["first_name"],
        "last_name": test_user_credentials["last_name"]
    }
    response = client.post("/api/v1/register", json=user_data)
    assert response.status_code == 204
    
    return (test_user_credentials["email"], test_user_credentials["password"])
