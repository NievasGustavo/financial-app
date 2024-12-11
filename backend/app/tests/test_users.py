def test_create_user(client):
    new_user = {
        "username": "testuser",
        "password": "testpassword",
        "email": "example@cordoba.com",
        "first_name": "Test",
        "last_name": "User",
        "age": 25
    }

    response = client.post("/users/", json=new_user)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == new_user["username"]
    assert "id" in data


def test_get_users(client):
    response = client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_user_by_id(client, test_user):
    response = client.get(f"/users/{test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.username
    

def test_update_user(client, test_user):
    new_user = {
        "username": "updateduser",
        "password": "testpassword",
        "email": "example@cordoba.com",
        "first_name": "Test",
        "last_name": "User",
        "age": 25
    }

    response = client.patch(f"/users/{test_user.id}", json=new_user)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_user["username"]


def test_delete_user(client, test_user):
    response = client.delete(f"/users/{test_user.id}")
    assert response.status_code == 204
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 404
