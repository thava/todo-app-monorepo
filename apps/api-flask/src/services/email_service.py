"""Email service (console output for development)"""
from flask import current_app


class EmailService:
    """Service for sending emails"""

    @staticmethod
    def send_verification_email(email: str, full_name: str, token: str):
        """Send email verification link"""
        base_url = current_app.config['BASE_URL']
        verification_url = f"{base_url}/auth/verify-email?token={token}"

        # In development, just log to console
        if current_app.config.get('EMAIL_ENABLED', False):
            # TODO: Implement actual email sending (SMTP, SendGrid, etc.)
            pass

        # Console output for development
        print(f"""
        =====================================
        EMAIL VERIFICATION
        =====================================
        To: {email}
        Name: {full_name}

        Click the link below to verify your email:
        {verification_url}

        Token: {token}
        =====================================
        """)

    @staticmethod
    def send_password_reset_email(email: str, full_name: str, token: str):
        """Send password reset link"""
        base_url = current_app.config['BASE_URL']
        reset_url = f"{base_url}/auth/reset-password?token={token}"

        # In development, just log to console
        if current_app.config.get('EMAIL_ENABLED', False):
            # TODO: Implement actual email sending
            pass

        # Console output for development
        print(f"""
        =====================================
        PASSWORD RESET
        =====================================
        To: {email}
        Name: {full_name}

        Click the link below to reset your password:
        {reset_url}

        Token: {token}
        =====================================
        """)

    @staticmethod
    def send_password_changed_email(email: str, full_name: str):
        """Send password changed confirmation"""
        # In development, just log to console
        if current_app.config.get('EMAIL_ENABLED', False):
            # TODO: Implement actual email sending
            pass

        # Console output for development
        print(f"""
        =====================================
        PASSWORD CHANGED CONFIRMATION
        =====================================
        To: {email}
        Name: {full_name}

        Your password has been successfully changed.
        If you did not make this change, please contact support immediately.
        =====================================
        """)
