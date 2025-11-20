"""Initialize database with default sysadmin user for development."""

import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import get_engine
from app.models.user import RoleEnum, User
from app.services.password import PasswordService


def create_sysadmin_user(session: Session, password_service: PasswordService) -> None:
    """Create sysadmin user if it doesn't exist (dev environment only)."""
    if settings.NODE_ENV != "development":
        return

    # Check if any sysadmin exists
    statement = select(User).where(User.role == RoleEnum.SYSADMIN)
    existing_sysadmin = session.exec(statement).first()

    if existing_sysadmin:
        print("Sysadmin user already exists")
        return

    # Create sysadmin1 user
    email = "sysadmin1@zatvia.com"
    password = "Todo####"  # Default demo password

    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()

    if existing_user:
        print(f"User {email} already exists")
        return

    # Hash password
    password_hash = password_service.hash_password(password)

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        full_name="System Administrator",
        password_hash_primary=password_hash,
        role=RoleEnum.SYSADMIN,
        email_verified_at=datetime.utcnow(),  # Auto-verify for dev
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(user)
    session.commit()
    print(f"Created sysadmin user: {email}")


def init() -> None:
    """Initialize database with default data."""
    engine = get_engine()

    with Session(engine) as session:
        password_service = PasswordService()
        create_sysadmin_user(session, password_service)


if __name__ == "__main__":
    init()
