"""Todo model"""
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedAsDataclass
import enum
from typing import TYPE_CHECKING

from ..app import db

if TYPE_CHECKING:
    from .user import User


class PriorityEnum(enum.Enum):
    """Todo priority levels"""
    low = 'low'
    medium = 'medium'
    high = 'high'

# Note: The class static variables are used to define 
#       metadata for marshmallow serialization. 
#       It internally defines __init__ method with matching parameters.
#       But during compile time since init method is missing,
#       pyright raises lots of type warnings/errors.
#       Using MappedAsDataclass, Mapped, mapped_column we help type checkers.
#       SqlAlchemy ORM has plugin for Pyright typechecker to recognize
#       the Mapped primitives to derive type information.
#
# FastAPI extensively uses Pydantic for data validation.
# Using dataclasses is an alternative to pydantic though less powerful.
# Marshmaloow is another alternative to pydantic for serialization and
# validation but the library/return value is untyped.
# This poses some challenges and you may employ any one of these:
# 1. Dummy wrapper functions that returns deterministic type
# 2. explicit casting and assert isinstance of some-type
#
# SqlAlchemy has not fully adopted dataclasses yet.
# 

class Todo(MappedAsDataclass, db.Model):
    """Todo model"""
    __tablename__ = 'todos'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, init=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(Text)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    priority: Mapped[PriorityEnum] = mapped_column(Enum(PriorityEnum), default=PriorityEnum.medium)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc), init=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc), init=False)

    # Relationships
    owner: Mapped["User"] = relationship('User', back_populates='todos', init=False)

    def __repr__(self):
        return f'<Todo {self.id}>'

    def to_dict(self, include_owner_info=False):
        """Convert to dictionary"""
        data = {
            'id': str(self.id),
            'ownerId': str(self.owner_id),
            'description': self.description,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority.value,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
        }
        if include_owner_info and self.owner:
            data['ownerEmail'] = self.owner.email
            data['ownerName'] = self.owner.full_name
            data['ownerRole'] = self.owner.role.value
        return data
