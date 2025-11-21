"""Email service for sending verification and notification emails."""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid or SMTP."""

    def __init__(self) -> None:
        """Initialize email service."""
        self.enabled = settings.emails_enabled
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME or settings.PROJECT_NAME

    def send_verification_email(self, to_email: str, full_name: str, token: str) -> None:
        """
        Send email verification link.

        Args:
            to_email: Recipient email address
            full_name: Recipient full name
            token: Verification token
        """
        if not self.enabled:
            logger.warning(f"Email not sent (emails disabled): verification to {to_email}")
            return

        verification_url = f"{settings.FRONTEND_HOST}/verify-email?token={token}"

        # TODO: Implement actual email sending using SendGrid or SMTP
        logger.info(f"Would send verification email to {to_email}: {verification_url}")

    def send_password_reset_email(self, to_email: str, full_name: str, token: str) -> None:
        """
        Send password reset link.

        Args:
            to_email: Recipient email address
            full_name: Recipient full name
            token: Password reset token
        """
        if not self.enabled:
            logger.warning(f"Email not sent (emails disabled): password reset to {to_email}")
            return

        reset_url = f"{settings.FRONTEND_HOST}/reset-password?token={token}"

        # TODO: Implement actual email sending using SendGrid or SMTP
        logger.info(f"Would send password reset email to {to_email}: {reset_url}")

    def send_password_changed_email(self, to_email: str, full_name: str) -> None:
        """
        Send password changed confirmation.

        Args:
            to_email: Recipient email address
            full_name: Recipient full name
        """
        if not self.enabled:
            logger.warning(f"Email not sent (emails disabled): password changed to {to_email}")
            return

        # TODO: Implement actual email sending using SendGrid or SMTP
        logger.info(f"Would send password changed email to {to_email}")
