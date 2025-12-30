"""add_uuid_defaults_to_id_columns

Revision ID: e69096ed52c0
Revises: 68ee137a5c84
Create Date: 2025-12-29 02:34:15.239825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e69096ed52c0'
down_revision: Union[str, Sequence[str], None] = '68ee137a5c84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add DEFAULT gen_random_uuid() to all UUID primary key columns."""

    # Add UUID generation default to all tables with UUID primary keys
    tables = [
        'users',
        'todos',
        'refresh_token_sessions',
        'password_reset_tokens',
        'email_verification_tokens',
    ]

    for table in tables:
        op.execute(f"""
            ALTER TABLE {table}
            ALTER COLUMN id SET DEFAULT gen_random_uuid()
        """)


def downgrade() -> None:
    """Remove DEFAULT gen_random_uuid() from UUID primary key columns."""

    # Remove UUID generation default from all tables
    tables = [
        'users',
        'todos',
        'refresh_token_sessions',
        'password_reset_tokens',
        'email_verification_tokens',
    ]

    for table in tables:
        op.execute(f"""
            ALTER TABLE {table}
            ALTER COLUMN id DROP DEFAULT
        """)
