"""Authentication endpoints"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from marshmallow import Schema, fields, validate, ValidationError

from ..app import db
from ..models.user import User, RoleEnum
from ..models.refresh_token_session import RefreshTokenSession
from ..models.email_verification_token import EmailVerificationToken
from ..models.password_reset_token import PasswordResetToken
from ..services import PasswordService, TokenService, EmailService, AuditService
from ..api.decorators import jwt_required_with_user

auth_bp = Blueprint('auth', __name__)


# Schemas
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    fullName = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    autoverify = fields.Bool(load_default=False)
    role = fields.Str(load_default='guest', validate=validate.OneOf(['guest', 'admin', 'sysadmin']))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class RefreshTokenSchema(Schema):
    refreshToken = fields.Str(required=True)


class RequestPasswordResetSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    newPassword = fields.Str(required=True, validate=validate.Length(min=8))


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = RegisterSchema().load(request.json)

    email = data['email'].lower().strip()
    password = data['password']
    full_name = data['fullName'].strip()
    autoverify = data.get('autoverify', False)
    role = data.get('role', 'guest')

    # Validate password strength
    password_validation = PasswordService.validate_password_strength(password, email)
    if not password_validation['is_valid']:
        return jsonify({
            'message': 'Password does not meet security requirements',
            'errors': password_validation['errors']
        }), 400

    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'User with this email already exists'}), 409

    # Create user
    password_hash = PasswordService.hash_password(password)
    new_user = User(
        email=email,
        full_name=full_name,
        password_hash_primary=password_hash,
        role=RoleEnum[role],
        email_verified_at=datetime.utcnow() if autoverify else None
    )
    db.session.add(new_user)
    db.session.commit()

    # Log registration
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    AuditService.log_auth(
        'REGISTER',
        str(new_user.id),
        {'email': new_user.email, 'role': new_user.role.value, 'autoverified': autoverify},
        ip_address,
        user_agent
    )

    # Send verification email if not autoverified
    if not autoverify:
        token = TokenService.generate_random_token()
        token_hash = TokenService.hash_token(token)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        verification_token = EmailVerificationToken(
            user_id=new_user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.session.add(verification_token)
        db.session.commit()

        EmailService.send_verification_email(new_user.email, new_user.full_name, token)

    return jsonify({
        'user': {
            'id': str(new_user.id),
            'email': new_user.email,
            'fullName': new_user.full_name,
            'role': new_user.role.value,
            'emailVerified': autoverify
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = LoginSchema().load(request.json)

    email = data['email'].lower().strip()
    password = data['password']

    # Find user
    user = User.query.filter_by(email=email).first()

    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    if not user:
        AuditService.log_auth(
            'LOGIN_FAILURE',
            None,
            {'email': email, 'reason': 'user_not_found'},
            ip_address,
            user_agent
        )
        return jsonify({'message': 'Invalid credentials'}), 401

    # Verify password
    if not PasswordService.verify_password(user.password_hash_primary, password):
        AuditService.log_auth(
            'LOGIN_FAILURE',
            str(user.id),
            {'email': email, 'reason': 'invalid_password'},
            ip_address,
            user_agent
        )
        return jsonify({'message': 'Invalid credentials'}), 401

    # Check email verification
    if not user.email_verified_at:
        AuditService.log_auth(
            'LOGIN_FAILURE',
            str(user.id),
            {'email': email, 'reason': 'email_not_verified'},
            ip_address,
            user_agent
        )
        return jsonify({'message': 'Please verify your email address before logging in'}), 401

    # Log successful login
    AuditService.log_auth(
        'LOGIN_SUCCESS',
        str(user.id),
        {'email': user.email},
        ip_address,
        user_agent
    )

    # Generate tokens
    access_token = TokenService.generate_access_token(
        str(user.id),
        {'email': user.email, 'role': user.role.value}
    )

    # Create refresh token session
    expires_at = datetime.utcnow() + timedelta(days=7)
    session = RefreshTokenSession(
        user_id=user.id,
        refresh_token_hash='',  # Will be updated below
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.session.add(session)
    db.session.flush()

    refresh_token = TokenService.generate_refresh_token(
        str(user.id),
        {'sessionId': str(session.id)}
    )
    session.refresh_token_hash = TokenService.hash_token(refresh_token)
    db.session.commit()

    return jsonify({
        'accessToken': access_token,
        'refreshToken': refresh_token,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'fullName': user.full_name,
            'role': user.role.value,
            'emailVerified': user.email_verified_at is not None
        }
    })


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    data = RefreshTokenSchema().load(request.json)
    refresh_token = data['refreshToken']

    # Verify refresh token signature using JWT_REFRESH_SECRET
    try:
        payload = TokenService.verify_refresh_token(refresh_token)
    except ValueError as e:
        return jsonify({'message': str(e)}), 401

    # Verify token hash in database
    token_hash = TokenService.hash_token(refresh_token)
    session = RefreshTokenSession.query.filter_by(refresh_token_hash=token_hash).first()

    if not session:
        return jsonify({'message': 'Invalid refresh token'}), 401

    if session.revoked_at:
        return jsonify({'message': 'Refresh token has been revoked'}), 401

    if datetime.utcnow() > session.expires_at:
        return jsonify({'message': 'Refresh token has expired'}), 401

    # Get user
    user = db.session.get(User, session.user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 401

    # Revoke old token (rotation)
    session.revoked_at = datetime.utcnow()
    db.session.commit()

    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    AuditService.log_auth(
        'REFRESH_TOKEN_ROTATED',
        str(user.id),
        {'sessionId': str(session.id)},
        ip_address,
        user_agent
    )

    # Generate new tokens
    access_token = TokenService.generate_access_token(
        str(user.id),
        {'email': user.email, 'role': user.role.value}
    )

    expires_at = datetime.utcnow() + timedelta(days=7)
    new_session = RefreshTokenSession(
        user_id=user.id,
        refresh_token_hash='',
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.session.add(new_session)
    db.session.flush()

    new_refresh_token = TokenService.generate_refresh_token(
        str(user.id),
        {'sessionId': str(new_session.id)}
    )
    new_session.refresh_token_hash = TokenService.hash_token(new_refresh_token)
    db.session.commit()

    return jsonify({
        'accessToken': access_token,
        'refreshToken': new_refresh_token,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'fullName': user.full_name,
            'role': user.role.value,
            'emailVerified': user.email_verified_at is not None
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    data = RefreshTokenSchema().load(request.json)
    refresh_token = data['refreshToken']

    token_hash = TokenService.hash_token(refresh_token)
    session = RefreshTokenSession.query.filter_by(refresh_token_hash=token_hash).first()

    if session:
        session.revoked_at = datetime.utcnow()
        db.session.commit()

        if session.user_id:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            AuditService.log_auth(
                'LOGOUT',
                str(session.user_id),
                {},
                ip_address,
                user_agent
            )

    return '', 204


@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    """Verify email with token"""
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token is required'}), 400

    token_hash = TokenService.hash_token(token)
    verification_token = EmailVerificationToken.query.filter_by(token_hash=token_hash).first()

    if not verification_token:
        return jsonify({'message': 'Invalid verification token'}), 400

    if datetime.utcnow() > verification_token.expires_at:
        return jsonify({'message': 'Verification token has expired'}), 400

    if verification_token.verified_at:
        return jsonify({'message': 'Email is already verified', 'alreadyVerified': True})

    # Mark token as used
    verification_token.verified_at = datetime.utcnow()

    # Mark user email as verified
    user = db.session.get(User, verification_token.user_id)
    if user:
        user.email_verified_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': 'Email verified successfully', 'alreadyVerified': False})


@auth_bp.route('/resend-verification', methods=['POST'])
@jwt_required_with_user
def resend_verification(user):
    """Resend verification email"""
    if user.email_verified_at:
        return jsonify({'message': 'Email already verified'}), 400

    # Delete old tokens
    EmailVerificationToken.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    # Create new token
    token = TokenService.generate_random_token()
    token_hash = TokenService.hash_token(token)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    verification_token = EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.session.add(verification_token)
    db.session.commit()

    EmailService.send_verification_email(user.email, user.full_name, token)

    return jsonify({'message': 'Verification email sent'})


@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset"""
    data = RequestPasswordResetSchema().load(request.json)
    email = data['email'].lower().strip()

    user = User.query.filter_by(email=email).first()

    # Always return success (security best practice)
    if not user:
        return jsonify({'message': 'Password reset request processed'})

    # Delete old tokens
    PasswordResetToken.query.filter_by(user_id=user.id).delete()

    # Create new token
    token = TokenService.generate_random_token()
    token_hash = TokenService.hash_token(token)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.session.add(reset_token)
    db.session.commit()

    EmailService.send_password_reset_email(user.email, user.full_name, token)

    return jsonify({'message': 'Password reset request processed'})


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = ResetPasswordSchema().load(request.json)
    token = data['token']
    new_password = data['newPassword']

    token_hash = TokenService.hash_token(token)
    reset_token = PasswordResetToken.query.filter_by(
        token_hash=token_hash,
        used_at=None
    ).first()

    if not reset_token:
        return jsonify({'message': 'Invalid or expired reset token'}), 400

    if datetime.utcnow() > reset_token.expires_at:
        return jsonify({'message': 'Reset token has expired'}), 400

    # Get user
    user = db.session.get(User, reset_token.user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 400

    # Validate password
    password_validation = PasswordService.validate_password_strength(new_password, user.email)
    if not password_validation['is_valid']:
        return jsonify({
            'message': 'Password does not meet security requirements',
            'errors': password_validation['errors']
        }), 400

    # Update password
    user.password_hash_primary = PasswordService.hash_password(new_password)
    reset_token.used_at = datetime.utcnow()

    # Revoke all refresh tokens
    RefreshTokenSession.query.filter_by(user_id=user.id).update({'revoked_at': datetime.utcnow()})

    db.session.commit()

    # Send confirmation email
    EmailService.send_password_changed_email(user.email, user.full_name)

    return jsonify({'message': 'Password reset successfully'})
