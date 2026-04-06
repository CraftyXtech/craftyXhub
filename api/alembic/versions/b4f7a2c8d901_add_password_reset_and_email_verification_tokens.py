"""add_password_reset_and_email_verification_tokens

Revision ID: b4f7a2c8d901
Revises: e3c2a7d9b123
Create Date: 2026-02-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b4f7a2c8d901"
down_revision = ("e3c2a7d9b123", "c59bc5397fda")
branch_labels = None
depends_on = None


def _existing_indexes(inspector, table_name: str) -> set[str]:
    if not inspector.has_table(table_name):
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _ensure_index(table_name: str, index_name: str, columns: list[str], *, unique: bool) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = _existing_indexes(inspector, table_name)
    if index_name in existing_indexes:
        return
    op.create_index(index_name, table_name, columns, unique=unique)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create password_reset_tokens table
    if not inspector.has_table("password_reset_tokens"):
        op.create_table(
            "password_reset_tokens",
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
            sa.Column("token", sa.String(length=255), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used", sa.Boolean(), server_default=sa.text("false"), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = sa.inspect(bind)
    _ensure_index(
        "password_reset_tokens",
        "ix_password_reset_tokens_user_id",
        ["user_id"],
        unique=False,
    )
    _ensure_index(
        "password_reset_tokens",
        "ix_password_reset_tokens_token",
        ["token"],
        unique=True,
    )
    _ensure_index(
        "password_reset_tokens",
        "ix_password_reset_tokens_uuid",
        ["uuid"],
        unique=True,
    )

    # Create email_verification_tokens table
    if not inspector.has_table("email_verification_tokens"):
        op.create_table(
            "email_verification_tokens",
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
            sa.Column("token", sa.String(length=255), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used", sa.Boolean(), server_default=sa.text("false"), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = sa.inspect(bind)
    _ensure_index(
        "email_verification_tokens",
        "ix_email_verification_tokens_user_id",
        ["user_id"],
        unique=False,
    )
    _ensure_index(
        "email_verification_tokens",
        "ix_email_verification_tokens_token",
        ["token"],
        unique=True,
    )
    _ensure_index(
        "email_verification_tokens",
        "ix_email_verification_tokens_uuid",
        ["uuid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_email_verification_tokens_uuid", table_name="email_verification_tokens")
    op.drop_index("ix_email_verification_tokens_token", table_name="email_verification_tokens")
    op.drop_index("ix_email_verification_tokens_user_id", table_name="email_verification_tokens")
    op.drop_table("email_verification_tokens")

    op.drop_index("ix_password_reset_tokens_uuid", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_token", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
