"""Test configuration and fixtures."""

import uuid
from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.db import get_engine
from app.main import app
from app.models.todo import PriorityEnum, Todo
from app.models.user import RoleEnum, User
from app.services.password import PasswordService


@pytest.fixture(name="session", scope="function")
def session_fixture() -> Generator[Session, None, None]:
    """Create a test database session.

    Uses the dev database instance as requested.
    Each test gets a fresh session within a transaction that's rolled back after the test.
    """
    engine = get_engine()
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def get_session_override() -> Generator[Session, None, None]:
        yield session

    from app.core.db import get_db
    app.dependency_overrides[get_db] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="password_service")
def password_service_fixture() -> PasswordService:
    """Create password service instance."""
    return PasswordService()


@pytest.fixture(name="guest_user")
def guest_user_fixture(session: Session, password_service: PasswordService) -> User:
    """Create a test guest user."""
    user = User(
        id=uuid.uuid4(),
        email="testguest@example.com",
        full_name="Test Guest",
        password_hash_primary=password_service.hash_password("Password123!"),
        role=RoleEnum.GUEST,
        email_verified_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session, password_service: PasswordService) -> User:
    """Create a test admin user."""
    user = User(
        id=uuid.uuid4(),
        email="testadmin@example.com",
        full_name="Test Admin",
        password_hash_primary=password_service.hash_password("Password123!"),
        role=RoleEnum.ADMIN,
        email_verified_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="sysadmin_user")
def sysadmin_user_fixture(session: Session, password_service: PasswordService) -> User:
    """Create a test sysadmin user."""
    user = User(
        id=uuid.uuid4(),
        email="testsysadmin@example.com",
        full_name="Test Sysadmin",
        password_hash_primary=password_service.hash_password("Password123!"),
        role=RoleEnum.SYSADMIN,
        email_verified_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="guest_token")
def guest_token_fixture(client: TestClient, guest_user: User) -> str:
    """Get access token for guest user."""
    response = client.post(
        "/auth/login",
        json={"email": "testguest@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    return response.json()["accessToken"]


@pytest.fixture(name="admin_token")
def admin_token_fixture(client: TestClient, admin_user: User) -> str:
    """Get access token for admin user."""
    response = client.post(
        "/auth/login",
        json={"email": "testadmin@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    return response.json()["accessToken"]


@pytest.fixture(name="sysadmin_token")
def sysadmin_token_fixture(client: TestClient, sysadmin_user: User) -> str:
    """Get access token for sysadmin user."""
    response = client.post(
        "/auth/login",
        json={"email": "testsysadmin@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    return response.json()["accessToken"]


@pytest.fixture(name="sample_todo")
def sample_todo_fixture(session: Session, guest_user: User) -> Todo:
    """Create a sample todo."""
    todo = Todo(
        id=uuid.uuid4(),
        owner_id=guest_user.id,
        description="Test todo",
        priority=PriorityEnum.MEDIUM,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def create_test_user(
    session: Session,
    password_service: PasswordService,
    email: str,
    full_name: str,
    role: RoleEnum = RoleEnum.GUEST,
    verified: bool = True,
) -> User:
    """Helper to create a test user."""
    user = User(
        id=uuid.uuid4(),
        email=email,
        full_name=full_name,
        password_hash_primary=password_service.hash_password("Password123!"),
        role=role,
        email_verified_at=datetime.utcnow() if verified else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_todo(
    session: Session,
    owner_id: uuid.UUID,
    description: str = "Test todo",
    priority: PriorityEnum = PriorityEnum.MEDIUM,
    due_date: datetime | None = None,
) -> Todo:
    """Helper to create a test todo."""
    todo = Todo(
        id=uuid.uuid4(),
        owner_id=owner_id,
        description=description,
        priority=priority,
        due_date=due_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
