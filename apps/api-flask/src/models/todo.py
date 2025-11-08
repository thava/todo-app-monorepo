"""Todo model"""
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

from ..app import db


class PriorityEnum(enum.Enum):
    """Todo priority levels"""
    low = 'low'
    medium = 'medium'
    high = 'high'


class Todo(db.Model):
    """Todo model"""
    __tablename__ = 'todos'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime(timezone=True), nullable=True)
    priority = db.Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.medium)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', back_populates='todos')

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
