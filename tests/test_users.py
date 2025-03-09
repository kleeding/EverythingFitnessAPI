import pytest
from app import schemas, models


def test_create_user(client, session):
    user_query = session.query(models.User).filter(models.User.username == "test")

    user_res = user_query.first()
    assert user_res == None

    res = client.post(
        "/users/",
        json={"username": "test", "email": "test@gmail.com", "password": "password123"},
    )
    user_res = user_query.first()
    assert user_res != None

    new_user = schemas.UserOut(**res.json())

    assert new_user.username == "test"
    assert res.status_code == 201


@pytest.mark.parametrize(
    "username, email, password",
    [
        (None, "test@gmail.com", "password123"),
        ("test", None, "password123"),
        ("test", "test@gmail.com", None),
    ],
)
def test_create_user_invalid_form(client, username, email, password):
    res = client.post(
        "/users/",
        json={"username": username, "email": email, "password": password},
    )

    assert res.status_code == 422


def test_get_user(authorized_client, test_user):
    res = authorized_client.get(f"/users/{test_user['id']}")

    assert res.status_code == 200


def test_get_user_invalid(authorized_client, test_user):
    res = authorized_client.get("/users/999999")

    assert res.status_code == 404
