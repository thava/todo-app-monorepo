"""Prepare schema for OAuth support

Revision ID: 68ee137a5c84
Revises: be1f008c1ab7
Create Date: 2025-12-29 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '68ee137a5c84'
down_revision: Union[str, None] = 'be1f008c1ab7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add OAuth fields and migrate existing data."""

    # Step 1: Add new columns
    op.add_column('users', sa.Column('contact_email', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('google_sub', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('google_email', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('ms_oid', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('ms_tid', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('ms_email', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('local_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('local_username', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('local_password_hash', sa.Text(), nullable=True))

    # Step 2: Migrate existing data (email -> local_username, password_hash_primary -> local_password_hash)
    op.execute("UPDATE users SET local_username = email")
    op.execute("UPDATE users SET local_password_hash = password_hash_primary")
    op.execute("UPDATE users SET local_enabled = true")

    # Step 3: Drop old columns
    op.drop_index('ix_users_email', table_name='users', if_exists=True)
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_column('users', 'email')
    op.drop_column('users', 'password_hash_primary')

    # Step 4: Add unique constraints
    op.create_unique_constraint('users_google_sub_unique', 'users', ['google_sub'])
    op.create_unique_constraint('users_local_username_unique', 'users', ['local_username'])
    op.create_unique_constraint('users_ms_identity_unique', 'users', ['ms_tid', 'ms_oid'])


def downgrade() -> None:
    """Revert OAuth preparation changes."""

    # Reverse Step 4: Drop unique constraints
    op.drop_constraint('users_ms_identity_unique', 'users', type_='unique')
    op.drop_constraint('users_local_username_unique', 'users', type_='unique')
    op.drop_constraint('users_google_sub_unique', 'users', type_='unique')

    # Reverse Step 3: Re-add old columns
    op.add_column('users', sa.Column('password_hash_primary', sa.Text(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=False, server_default=''))

    # Reverse Step 2: Migrate data back
    op.execute("UPDATE users SET email = local_username")
    op.execute("UPDATE users SET password_hash_primary = local_password_hash")

    # Restore constraints and indexes
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.create_index('ix_users_email', 'users', ['email'], if_not_exists=True)

    # Reverse Step 1: Drop new columns
    op.drop_column('users', 'local_password_hash')
    op.drop_column('users', 'local_username')
    op.drop_column('users', 'local_enabled')
    op.drop_column('users', 'ms_email')
    op.drop_column('users', 'ms_tid')
    op.drop_column('users', 'ms_oid')
    op.drop_column('users', 'google_email')
    op.drop_column('users', 'google_sub')
    op.drop_column('users', 'contact_email')
