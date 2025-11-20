"""Initial migration

Revision ID: b89ca7d6aaef
Revises:
Create Date: 2025-11-21 00:01:16.247758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b89ca7d6aaef'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum types
    role_enum = postgresql.ENUM('guest', 'admin', 'sysadmin', name='roleenum')
    role_enum.create(op.get_bind())

    priority_enum = postgresql.ENUM('low', 'medium', 'high', name='priorityenum')
    priority_enum.create(op.get_bind())

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('fullName', sa.String(length=255), nullable=False),
        sa.Column('passwordHashPrimary', sa.Text(), nullable=False),
        sa.Column('role', role_enum, nullable=False, server_default='guest'),
        sa.Column('emailVerifiedAt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create refresh_token_sessions table
    op.create_table(
        'refresh_token_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('userId', sa.UUID(), nullable=False),
        sa.Column('refreshTokenHash', sa.Text(), nullable=False),
        sa.Column('userAgent', sa.Text(), nullable=True),
        sa.Column('ipAddress', sa.String(length=45), nullable=True),
        sa.Column('expiresAt', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revokedAt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('userId', sa.UUID(), nullable=False),
        sa.Column('tokenHash', sa.Text(), nullable=False),
        sa.Column('expiresAt', sa.DateTime(timezone=True), nullable=False),
        sa.Column('usedAt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('userId', sa.UUID(), nullable=False),
        sa.Column('tokenHash', sa.Text(), nullable=False),
        sa.Column('expiresAt', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verifiedAt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('ownerId', sa.UUID(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('dueDate', sa.DateTime(timezone=True), nullable=True),
        sa.Column('priority', priority_enum, nullable=False, server_default='medium'),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['ownerId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('todos')
    op.drop_table('email_verification_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('refresh_token_sessions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    # Drop enum types
    priority_enum = postgresql.ENUM('low', 'medium', 'high', name='priorityenum')
    priority_enum.drop(op.get_bind())

    role_enum = postgresql.ENUM('guest', 'admin', 'sysadmin', name='roleenum')
    role_enum.drop(op.get_bind())
