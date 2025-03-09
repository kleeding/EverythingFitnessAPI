import pytest
from jose import jwt
from app import schemas
from app.config import settings
from datetime import datetime, timedelta


def test_login(client, test_user):
    res = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )

    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=settings.algorithm
    )

    expire_time = datetime.timestamp(
        datetime.now() + timedelta(0, settings.access_token_expire_minutes * 60)
    )

    assert payload["user_id"] == test_user["id"]
    assert payload["exp"] <= expire_time


@pytest.mark.parametrize(
    "username, password",
    [
        ("invalid_test", "password123"),
        ("test", "invalid_password123"),
        (None, "password123"),
        ("test", None),
    ],
)
def test_login_invalid(client, test_user, username, password):
    res = client.post(
        "/login",
        data={"username": username, "password": password},
    )

    assert res.status_code == 403
