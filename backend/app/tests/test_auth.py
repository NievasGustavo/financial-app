import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import User
from app.utils.auth import get_password_hash

client = TestClient(app)

@pytest.fixture
def test_user(session):
    user = User(
        username="testuser",
        email="test@example.com", 
        password=get_password_hash("testpassword"),
        first_name="Test",
        last_name="User",
        age=25
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_login_success(client, test_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "wronguser",
            "password": "wrongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_current_user(client, test_user):
    login_response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword",
            "scope": "me"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_complete_registration_invalid_data(client):
    response = client.post(
        "/auth/google/complete-registration",
        json={
            "google_data": {},
            "user_data": {"age": -1}
        }
    )

    assert response.status_code == 400
    assert "error" in response.json() or "detail" in response.json()



def test_get_current_user_invalid_token(client):
    response = client.get(
        "/auth/users/me/",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_google_login_redirect(client):
    response = client.get("/auth/google/login", follow_redirects=False)
    
    assert response.status_code == 307
    assert "accounts.google.com" in response.headers["location"]


def test_google_callback_missing_code(client):
    response = client.get("/auth/google/callback")
    
    assert response.status_code == 422


def test_google_callback_invalid_code(client):
    response = client.get("/auth/google/callback?code=invalid_code")
    
    assert response.status_code == 400


def test_complete_registration_invalid_data(client):
    response = client.post(
        "/auth/google/complete-registration",
        json={
            "google_data": {},
            "user_data": {"age": -1}
        }
    )

    assert response.status_code == 400
    assert "error" in response.json() or "detail" in response.json()


def test_complete_registration_missing_required_fields(client):
    response = client.post(
        "/auth/google/complete-registration",
        json={}
    )

    assert response.status_code == 422