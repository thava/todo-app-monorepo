"""Audit logging service"""
from ..app import db
from ..models.audit_log import AuditLog


class AuditService:
    """Service for audit logging"""

    @staticmethod
    def log_auth(action: str, user_id: str = None, metadata: dict = None,
                 ip_address: str = None, user_agent: str = None):
        """Log authentication event"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type='auth',
            meta=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()

    @staticmethod
    def log_action(action: str, user_id: str, entity_type: str = None,
                   entity_id: str = None, metadata: dict = None,
                   ip_address: str = None, user_agent: str = None):
        """Log user action"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
