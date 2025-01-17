from uuid import UUID
def test_create_user_success(client):
    new_user = {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "age": 25
    }

    response = client.post("/users/", json=new_user)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == new_user["username"]
    assert data["email"] == new_user["email"]
    assert "id" in data
    assert isinstance(UUID(data["id"]), UUID)


def test_create_user_duplicate_email(client, test_user):
    new_user = {
        "username": "different_user",
        "password": "testpassword",
        "email": test_user.email,
        "first_name": "Test",
        "last_name": "User",
        "age": 25
    }

    response = client.post("/users/", json=new_user)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_create_user_duplicate_username(client, test_user):
    new_user = {
        "username": test_user.username,
        "password": "testpassword",
        "email": "different@example.com",
        "first_name": "Test",
        "last_name": "User",
        "age": 25
    }

    response = client.post("/users/", json=new_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_create_user_invalid_email(client):
    new_user = {
        "username": "testuser",
        "password": "testpassword",
        "email": "invalid-email",
        "first_name": "Test",
        "last_name": "User",
        "age": 25
    }
    response = client.post("/users/", json=new_user)
    assert response.status_code == 422


def test_create_user_invalid_age(client):
    new_user = {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "age": -1
    }

    response = client.post("/users/", json=new_user)

    assert response.status_code == 422


def test_get_users_empty(client):
    response = client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_users_with_data(client, test_user):
    response = client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(user["id"] == str(test_user.id) for user in data)


def test_get_user_by_id_success(client, test_user):
    response = client.get(f"/users/{test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_get_user_by_id_not_found(client):
    random_uuid = UUID('12345678-1234-5678-1234-567812345678')
    response = client.get(f"/users/{random_uuid}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_success(client, test_user):
    update_data = {
        "username": "updated_user",
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "User",
        "age": 30
    }

    response = client.patch(f"/users/{test_user.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]
    assert data["age"] == update_data["age"]


def test_update_user_partial(client, test_user):
    update_data = {
        "username": "partial_update"
    }

    response = client.patch(f"/users/{test_user.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["email"] == test_user.email


def test_update_user_not_found(client):
    random_uuid = UUID('12345678-1234-5678-1234-567812345678')
    update_data = {"username": "new_username"}

    response = client.patch(f"/users/{random_uuid}", json=update_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_success(client, test_user):
    response = client.delete(f"/users/{test_user.id}")
    assert response.status_code == 204

    get_response = client.get(f"/users/{test_user.id}")
    assert get_response.status_code == 404


def test_delete_user_not_found(client):
    random_uuid = UUID('12345678-1234-5678-1234-567812345678')
    response = client.delete(f"/users/{random_uuid}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_invalid_email(client, test_user):
    update_data = {
        "email": "invalid-email"
    }

    response = client.patch(f"/users/{test_user.id}", json=update_data)

    assert response.status_code == 422


def test_update_user_invalid_age(client, test_user):
    update_data = {
        "age": -1
    }

    response = client.patch(f"/users/{test_user.id}", json=update_data)

    assert response.status_code == 422