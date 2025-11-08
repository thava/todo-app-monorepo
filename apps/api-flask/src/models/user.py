"""User model"""
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
import enum

from ..app import db


class RoleEnum(enum.Enum):
    """User roles"""
    guest = 'guest'
    admin = 'admin'
    sysadmin = 'sysadmin'


class User(db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255), nullable=False)
    password_hash_primary = db.Column(db.Text, nullable=False)
    role = db.Column(Enum(RoleEnum), nullable=False, default=RoleEnum.guest)
    email_verified_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    todos = db.relationship('Todo', back_populates='owner', cascade='all, delete-orphan')
    refresh_token_sessions = db.relationship('RefreshTokenSession', back_populates='user', cascade='all, delete-orphan')
    email_verification_tokens = db.relationship('EmailVerificationToken', back_populates='user', cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', back_populates='user', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self, include_timestamps=True):
        """Convert to dictionary"""
        data = {
            'id': str(self.id),
            'email': self.email,
            'fullName': self.full_name,
            'role': self.role.value,
            'emailVerified': self.email_verified_at is not None,
        }
        if include_timestamps:
            data['emailVerifiedAt'] = self.email_verified_at.isoformat() if self.email_verified_at else None
            data['createdAt'] = self.created_at.isoformat()
            data['updatedAt'] = self.updated_at.isoformat()
        return data
