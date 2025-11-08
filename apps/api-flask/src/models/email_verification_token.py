"""Email verification token model"""
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

from ..app import db


class EmailVerificationToken(db.Model):
    """Email verification token model"""
    __tablename__ = 'email_verification_tokens'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    verified_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='email_verification_tokens')

    def __repr__(self):
        return f'<EmailVerificationToken {self.id}>'
