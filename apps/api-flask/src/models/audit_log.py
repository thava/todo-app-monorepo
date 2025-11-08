"""Audit log model"""
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB

from ..app import db


class AuditLog(db.Model):
    """Audit log model"""
    __tablename__ = 'audit_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(UUID(as_uuid=True), nullable=True)
    # 'metadata' is reserved in SQLAlchemy, so we use 'meta' as attribute name
    # but map it to the 'metadata' column in the database
    meta = db.Column('metadata', JSONB, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'
