"""Test fixtures: in-memory sqlite via dependency override.

Environment variables are set before any application import so the
settings object validates, then the database dependency is overridden
with an isolated engine. Every test gets a fresh schema.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./unused_boot.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from social_media.database import Base, get_db
from social_media.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=test_engine, autoflush=False,
                              autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=test_engine)


def register(client, email, password="secret123", **extra):
    response = client.post("/users", json={"email": email,
                                           "password": password, **extra})
    assert response.status_code == 201, response.text
    data = response.json()
    data["password"] = password
    return data


def login_headers(client, email, password):
    response = client.post("/login", data={"username": email,
                                           "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def register_user(client):
    """Callable fixture so test modules never import conftest directly:
    a direct import would load this module twice and split the engine."""
    def _register(email, password="secret123", **extra):
        return register(client, email, password, **extra)
    return _register


@pytest.fixture()
def login_as(client):
    def _login(email, password):
        return login_headers(client, email, password)
    return _login


@pytest.fixture()
def user_one(client):
    return register(client, "moon@test.dev")


@pytest.fixture()
def user_two(client):
    return register(client, "other@test.dev")


@pytest.fixture()
def auth_one(client, user_one):
    return login_headers(client, user_one["email"], user_one["password"])


@pytest.fixture()
def auth_two(client, user_two):
    return login_headers(client, user_two["email"], user_two["password"])


@pytest.fixture()
def sample_post(client, auth_one):
    response = client.post("/posts", headers=auth_one, json={
        "title": "first post", "content": "hello"})
    assert response.status_code == 201, response.text
    return response.json()
