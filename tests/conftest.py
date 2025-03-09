from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "password123",
    }
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {
        "username": "test1",
        "email": "test2@gmail.com",
        "password": "password124",
    }
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    # post list contains 12 posts each by test_user 1 and 2,
    # 6 public and 6 private
    posts_data = posts_data = [
        {"title": "1st - u1 pub", "private": False, "owner_id": test_user["id"]},
        {"title": "2nd - u1 pub", "private": False, "owner_id": test_user["id"]},
        {"title": "3rd - u1 pub", "private": False, "owner_id": test_user["id"]},
        {"title": "4th - u1 pub", "private": False, "owner_id": test_user["id"]},
        {"title": "5th - u1 pub", "private": False, "owner_id": test_user["id"]},
        {"title": "6th - u1 pub", "private": False, "owner_id": test_user["id"]},
        {"title": "1st - u1 pri", "private": True, "owner_id": test_user["id"]},
        {"title": "2nd - u1 pri", "private": True, "owner_id": test_user["id"]},
        {"title": "3rd - u1 pri", "private": True, "owner_id": test_user["id"]},
        {"title": "4th - u1 pri", "private": True, "owner_id": test_user["id"]},
        {"title": "5th - u1 pri", "private": True, "owner_id": test_user["id"]},
        {"title": "6th - u1 pri", "private": True, "owner_id": test_user["id"]},
        {"title": "1st - u2 pub", "private": False, "owner_id": test_user2["id"]},
        {"title": "2nd - u2 pub", "private": False, "owner_id": test_user2["id"]},
        {"title": "3rd - u2 pub", "private": False, "owner_id": test_user2["id"]},
        {"title": "4th - u2 pub", "private": False, "owner_id": test_user2["id"]},
        {"title": "5th - u2 pub", "private": False, "owner_id": test_user2["id"]},
        {"title": "6th - u2 pub", "private": False, "owner_id": test_user2["id"]},
        {"title": "1st - u2 pri", "private": True, "owner_id": test_user2["id"]},
        {"title": "2nd - u2 pri", "private": True, "owner_id": test_user2["id"]},
        {"title": "3rd - u2 pri", "private": True, "owner_id": test_user2["id"]},
        {"title": "4th - u2 pri", "private": True, "owner_id": test_user2["id"]},
        {"title": "5th - u2 pri", "private": True, "owner_id": test_user2["id"]},
        {"title": "6th - u2 pri", "private": True, "owner_id": test_user2["id"]},
    ]

    def create_post(post):
        return models.Post(content="test_content", **post)

    post_map = map(create_post, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()

    posts = session.query(models.Post).all()
    return posts
