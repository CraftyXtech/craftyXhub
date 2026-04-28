"""add_homepage_trending_posts

Revision ID: c1d2e3f4a5b6
Revises: b8c9d0e1f2a3
Create Date: 2026-04-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c1d2e3f4a5b6"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column(
            "is_homepage_trending",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column("posts", sa.Column("homepage_trending_order", sa.Integer(), nullable=True))
    op.add_column("posts", sa.Column("homepage_trending_picked_at", sa.DateTime(), nullable=True))
    op.create_index(
        op.f("ix_posts_homepage_trending_order"),
        "posts",
        ["is_homepage_trending", "homepage_trending_order"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_posts_homepage_trending_order"), table_name="posts")
    op.drop_column("posts", "homepage_trending_picked_at")
    op.drop_column("posts", "homepage_trending_order")
    op.drop_column("posts", "is_homepage_trending")
