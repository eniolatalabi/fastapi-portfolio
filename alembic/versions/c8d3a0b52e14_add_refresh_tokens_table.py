"""Add the refresh_tokens table.

Server-side refresh token records enable rotation on every use,
revocation on logout, and reuse detection.

Revision ID: c8d3a0b52e14
Revises: b7c2f9a41d03
"""
import sqlalchemy as sa
from alembic import op

revision = "c8d3a0b52e14"
down_revision = "b7c2f9a41d03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "refresh_tokens",
        sa.Column("jti", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default=sa.text("false"),
                  nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("jti"),
    )


def downgrade():
    op.drop_table("refresh_tokens")
