"""Refresh token session model"""
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

from ..app import db


class RefreshTokenSession(db.Model):
    """Refresh token session model"""
    __tablename__ = 'refresh_token_sessions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    refresh_token_hash = db.Column(db.Text, nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='refresh_token_sessions')

    def __repr__(self):
        return f'<RefreshTokenSession {self.id}>'
