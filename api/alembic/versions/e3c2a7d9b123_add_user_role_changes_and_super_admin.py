"""add_user_role_changes_and_super_admin

Revision ID: e3c2a7d9b123
Revises: c32e7f61e440
Create Date: 2025-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e3c2a7d9b123"
down_revision = "c32e7f61e440"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # Extend the existing userrole enum in Postgres to include SUPER_ADMIN
    if dialect_name == "postgresql":
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'SUPER_ADMIN';")

    # Create user_role_changes audit table
    op.create_table(
        "user_role_changes",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), nullable=False),
        sa.Column("old_role", sa.String(length=50), nullable=False),
        sa.Column("new_role", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_user_role_changes_user_id", "user_role_changes", ["user_id"], unique=False
    )
    op.create_index(
        "ix_user_role_changes_changed_by_id",
        "user_role_changes",
        ["changed_by_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_role_changes_uuid", "user_role_changes", ["uuid"], unique=True
    )
    op.create_index(
        "ix_user_role_changes_created_at",
        "user_role_changes",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop audit table and its indexes
    op.drop_index("ix_user_role_changes_created_at", table_name="user_role_changes")
    op.drop_index("ix_user_role_changes_uuid", table_name="user_role_changes")
    op.drop_index("ix_user_role_changes_changed_by_id", table_name="user_role_changes")
    op.drop_index("ix_user_role_changes_user_id", table_name="user_role_changes")
    op.drop_table("user_role_changes")

    # Note: we intentionally do NOT remove the SUPER_ADMIN value from the userrole enum,
    # as Postgres does not support dropping enum values safely in a simple, portable way.


