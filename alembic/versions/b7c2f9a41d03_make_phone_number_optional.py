"""Make users.phone_number optional.

The column was NOT NULL with no API input path, which made user
registration violate its own schema. It is now a nullable profile
field exposed through the user schemas and the /users/me endpoints.

Revision ID: b7c2f9a41d03
Revises: 2f1913eedf1a
"""
import sqlalchemy as sa
from alembic import op

revision = "b7c2f9a41d03"
down_revision = "2f1913eedf1a"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("users", "phone_number",
                    existing_type=sa.String(), nullable=True)


def downgrade():
    # Will fail if null phone numbers exist; backfill before downgrading.
    op.alter_column("users", "phone_number",
                    existing_type=sa.String(), nullable=False)
