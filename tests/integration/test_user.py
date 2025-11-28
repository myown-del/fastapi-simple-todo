import pytest
from app.models.user import User


@pytest.mark.asyncio
async def test_register_user_creates_in_database(client, test_user_credentials):
    user_data = {
        "email": test_user_credentials["email"],
        "password": test_user_credentials["password"],
        "first_name": test_user_credentials["first_name"],
        "last_name": test_user_credentials["last_name"]
    }
    response = client.post("/api/v1/register", json=user_data)
    
    assert response.status_code == 204
    
    user_in_db = await User.filter(email=test_user_credentials["email"]).first()
    assert user_in_db is not None
    assert user_in_db.email == test_user_credentials["email"]
    assert user_in_db.first_name == test_user_credentials["first_name"]
    assert user_in_db.last_name == test_user_credentials["last_name"]
    assert user_in_db.password_hash is not None
    assert user_in_db.password_hash != test_user_credentials["password"]


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client, registered_user, test_user_credentials):
    user_data = {
        "email": test_user_credentials["email"],
        "password": "different_password",
        "first_name": "Different",
        "last_name": "Person"
    }
    response = client.post("/api/v1/register", json=user_data)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
    
    user_count = await User.filter(email=test_user_credentials["email"]).count()
    assert user_count == 1


@pytest.mark.asyncio
async def test_authenticate_user_with_valid_credentials(client, registered_user):
    email, password = registered_user
    
    response = client.get(
        "/api/v1/__user__",
        auth=(email, password)
    )
    
    assert response.status_code == 200
    assert response.json()["username"] == email


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_credentials(client, registered_user):
    email, _ = registered_user
    
    response = client.get(
        "/api/v1/__user__",
        auth=(email, "wrongpassword")
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
