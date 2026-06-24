import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.database import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models import Comment, RefreshToken, Task, TaskHistory, User

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
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def users(db_session):
    admin = User(
        name="Admin",
        email="admin@example.com",
        password_hash=hash_password("password123"),
        role="admin",
    )
    manager = User(
        name="Manager",
        email="manager@example.com",
        password_hash=hash_password("password123"),
        role="manager",
    )
    employee = User(
        name="Employee",
        email="employee@example.com",
        password_hash=hash_password("password123"),
        role="employee",
    )
    other_employee = User(
        name="Other Employee",
        email="other@example.com",
        password_hash=hash_password("password123"),
        role="employee",
    )
    db_session.add_all([admin, manager, employee, other_employee])
    db_session.commit()

    for user in [admin, manager, employee, other_employee]:
        db_session.refresh(user)

    return {
        "admin": admin,
        "manager": manager,
        "employee": employee,
        "other_employee": other_employee,
    }


def auth_headers(client, email: str, password: str = "password123") -> dict[str, str]:
    response = client.post(
        "/api/v1/login",
        json={"email": email, "password": password},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
