from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.database import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models import User
from app.services.cache import task_cache
from app.services.notifications import set_notification_session_factory

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    task_cache._local.clear()
    set_notification_session_factory(TestingSessionLocal)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        task_cache._local.clear()
        set_notification_session_factory(TestingSessionLocal)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def users(db_session):
    alice = User(
        name="Alice",
        email="alice@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    bob = User(
        name="Bob",
        email="bob@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    assignee = User(
        name="Assignee",
        email="assignee@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    admin = User(
        name="Admin",
        email="admin@example.com",
        password_hash=hash_password("password123"),
        role="admin",
    )
    db_session.add_all([alice, bob, assignee, admin])
    db_session.commit()
    for user in [alice, bob, assignee, admin]:
        db_session.refresh(user)
    return {"alice": alice, "bob": bob, "assignee": assignee, "admin": admin}


def auth_headers(client: TestClient, email: str, password: str = "password123") -> dict[str, str]:
    response = client.post(
        "/api/v1/login",
        data={"username": email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_project(client: TestClient, headers: dict[str, str], name: str = "Launch") -> dict:
    response = client.post(
        "/api/v1/projects",
        json={"name": name, "description": "Launch plan"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["data"]
