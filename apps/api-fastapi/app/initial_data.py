"""Initialize database with default sysadmin user for development."""

import logging
import uuid
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import get_engine
from app.models.user import RoleEnum, User
from app.services.password import PasswordService

logger = logging.getLogger(__name__)

def create_sysadmin_user(session: Session, password_service: PasswordService) -> None:
    """Create sysadmin user if it doesn't exist (dev environment only)."""
    if settings.NODE_ENV != "development":
        return

    # Check if any sysadmin exists
    statement = select(User).where(User.role == RoleEnum.SYSADMIN)
    existing_sysadmin = session.exec(statement).first()

    if existing_sysadmin:
        logger.info("Sysadmin user already exists")
        return

    # Create sysadmin1 user
    username = "sysadmin1@zatvia.com"
    password = "Todo####"  # Default demo password

    statement = select(User).where(User.local_username == username)
    existing_user = session.exec(statement).first()

    if existing_user:
        logger.info(f"User {username} already exists")
        return

    # Hash password
    password_hash = password_service.hash_password(password)

    user = User(
        id=uuid.uuid4(),
        local_username=username,
        full_name="System Administrator",
        local_password_hash=password_hash,
        local_enabled=True,
        role=RoleEnum.SYSADMIN,
        email_verified_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    session.add(user)
    session.commit()
    logger.info(f"Created sysadmin user: {username}")


def init() -> None:
    """Initialize database with default data."""
    engine = get_engine()

    with Session(engine) as session:
        password_service = PasswordService()
        create_sysadmin_user(session, password_service)


if __name__ == "__main__":
    init()
