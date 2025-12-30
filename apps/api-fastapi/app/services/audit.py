"""Audit service for logging user actions."""

import uuid
from typing import Any

from sqlmodel import Session

from app.models.audit import AuditLog


class AuditService:
    """Service for logging audit events."""

    def __init__(self, session: Session):
        """Initialize audit service."""
        self.session = session

    def log(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        meta: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Log an audit event.

        Never throws errors to avoid breaking app flow.
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                meta=meta,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.session.add(audit_log)
            self.session.commit()
        except Exception as e:
            # Log error but don't throw - audit failures shouldn't break app
            print(f"Audit logging failed: {e}")
            self.session.rollback()

    def log_auth(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        meta: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Log authentication event."""
        self.log(
            action=action,
            user_id=user_id,
            entity_type="auth",
            meta=meta,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def log_admin(
        self,
        action: str,
        admin_user_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        meta: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Log admin action."""
        self.log(
            action=action,
            user_id=admin_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            meta=meta,
            ip_address=ip_address,
            user_agent=user_agent,
        )
