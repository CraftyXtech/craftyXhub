"""add_newsletter_subscribers

Revision ID: b8c9d0e1f2a3
Revises: a9c3d4e5f6b7
Create Date: 2026-04-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b8c9d0e1f2a3"
down_revision = "a9c3d4e5f6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "newsletter_subscribers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False, server_default="homepage"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_newsletter_subscribers_uuid"), "newsletter_subscribers", ["uuid"], unique=True)
    op.create_index(op.f("ix_newsletter_subscribers_email"), "newsletter_subscribers", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_newsletter_subscribers_email"), table_name="newsletter_subscribers")
    op.drop_index(op.f("ix_newsletter_subscribers_uuid"), table_name="newsletter_subscribers")
    op.drop_table("newsletter_subscribers")
