#!/usr/bin/env python3
"""
Interactive Python shell with app context.

Provides convenient access to models, services, and database session.
"""

import code
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_engine
from app.services.auth import AuthService
from app.services.jwt import JWTService
from app.services.password import PasswordService

# Create database session
engine = get_engine()
db = Session(engine)

# Create service instances
password_service = PasswordService()
jwt_service = JWTService()
auth_service = AuthService(db, password_service, jwt_service)

# Banner
banner = f"""
FastAPI Todo App - Interactive Shell
=====================================

Available objects:
  - db: Database session (SQLModel Session)
  - settings: App settings
  - Models: User, Todo, RefreshTokenSession, PasswordResetToken, EmailVerificationToken
  - Enums: RoleEnum, PriorityEnum
  - Services: password_service, jwt_service, auth_service

Database: {settings.DATABASE_URL}

Example usage:
  >>> users = db.exec(select(User)).all()
  >>> todos = db.exec(select(Todo).where(Todo.priority == PriorityEnum.HIGH)).all()
  >>> user = db.exec(select(User).where(User.email == "test@example.com")).first()
"""

# Import select for convenience

# Start interactive shell
code.interact(banner=banner, local=locals())
