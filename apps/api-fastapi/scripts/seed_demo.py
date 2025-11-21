#!/usr/bin/env python3
"""Seed database with demo data for testing."""

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models.todo import PriorityEnum, Todo
from app.models.user import RoleEnum, User
from app.services.password import PasswordService

DOMAIN = 'domain.com'

def main() -> None:
    """Seed database with demo data."""
    print("🌱 Seeding database with demo data...")

    engine = get_engine()
    password_service = PasswordService()

    with Session(engine) as session:
        # Demo users configuration
        demo_users = [
            {
                "email": f"guest1@{DOMAIN}",
                "full_name": "Guest User 1",
                "role": RoleEnum.GUEST,
                "password": "Todo####",
            },
            {
                "email": f"guest2@{DOMAIN}",
                "full_name": "Guest User 2",
                "role": RoleEnum.GUEST,
                "password": "Todo####",
            },
            {
                "email": f"admin1@{DOMAIN}",
                "full_name": "Admin User 1",
                "role": RoleEnum.ADMIN,
                "password": "Todo####",
            },
            {
                "email": f"admin2@{DOMAIN}",
                "full_name": "Admin User 2",
                "role": RoleEnum.ADMIN,
                "password": "Todo####",
            },
        ]

        created_users = []

        # Create users
        for user_data in demo_users:
            existing = session.exec(
                select(User).where(User.email == user_data["email"])
            ).first()

            if existing:
                print(f"  ⏭  User already exists: {user_data['email']}")
                created_users.append(existing)
                continue

            user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash_primary=password_service.hash_password(
                    user_data["password"]
                ),
                role=user_data["role"],
                email_verified_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(user)
            created_users.append(user)
            print(f"  ✓ Created user: {user_data['email']} ({user_data['role'].value})")

        session.commit()

        # Refresh users to get IDs
        for user in created_users:
            session.refresh(user)

        # Create todos for guest users
        guest_users = [u for u in created_users if u.role == RoleEnum.GUEST]

        demo_todos = [
            {
                "description": "Buy groceries for the week",
                "priority": PriorityEnum.HIGH,
                "due_date": datetime.utcnow() + timedelta(days=2),
            },
            {
                "description": "Complete project documentation",
                "priority": PriorityEnum.MEDIUM,
                "due_date": datetime.utcnow() + timedelta(days=7),
            },
            {
                "description": "Call dentist for appointment",
                "priority": PriorityEnum.LOW,
                "due_date": None,
            },
            {
                "description": "Review pull requests",
                "priority": PriorityEnum.HIGH,
                "due_date": datetime.utcnow() + timedelta(days=1),
            },
            {
                "description": "Plan team meeting agenda",
                "priority": PriorityEnum.MEDIUM,
                "due_date": datetime.utcnow() + timedelta(days=3),
            },
        ]

        for i, user in enumerate(guest_users):
            # Create 2-3 todos per user
            todos_for_user = demo_todos[i * 2 : (i * 2) + 3]

            for todo_data in todos_for_user:
                todo = Todo(
                    id=uuid.uuid4(),
                    owner_id=user.id,
                    description=todo_data["description"],
                    priority=todo_data["priority"],
                    due_date=todo_data["due_date"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(todo)
                print(
                    f"  ✓ Created todo for {user.email}: {todo_data['description']}"
                )

        session.commit()

    print("\n✅ Database seeded successfully!")
    print("\nDemo credentials:")
    print(f"  Email: guest1@{DOMAIN}")
    print(f"  Email: admin1@{DOMAIN}")
    print(f"  Email: sysadmin1@{DOMAIN}")


if __name__ == "__main__":
    main()
