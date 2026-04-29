"""add_site_settings_and_breaking_news

Revision ID: d4e5f6a7b8c9
Revises: c1d2e3f4a5b6
Create Date: 2026-04-29 12:00:00.000000
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("uuid", sa.String(length=36), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("singleton_key", sa.String(length=32), nullable=False, unique=True),
        sa.Column("site_name", sa.String(length=120), nullable=False),
        sa.Column("site_description", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("posts_per_page", sa.Integer(), nullable=False),
        sa.Column("allow_comments", sa.Boolean(), nullable=False),
        sa.Column("allow_registration", sa.Boolean(), nullable=False),
        sa.Column("require_email_verification", sa.Boolean(), nullable=False),
        sa.Column("identity_label", sa.String(length=80), nullable=False),
        sa.Column("breaking_label", sa.String(length=80), nullable=False),
        sa.Column("daily_brief_label", sa.String(length=80), nullable=False),
        sa.Column("daily_brief_url", sa.String(length=255), nullable=False),
        sa.Column("social_links", sa.JSON(), nullable=False),
        sa.Column("ad_slot", sa.JSON(), nullable=False),
        sa.Column("market_watchlist", sa.JSON(), nullable=False),
        sa.Column("market_cache", sa.JSON(), nullable=False),
        sa.Column("market_cache_updated_at", sa.DateTime(), nullable=True),
        sa.Column("spotlight_items", sa.JSON(), nullable=False),
    )
    op.create_index(op.f("ix_site_settings_uuid"), "site_settings", ["uuid"], unique=True)

    op.bulk_insert(
        sa.table(
            "site_settings",
            sa.column("uuid", sa.String),
            sa.column("singleton_key", sa.String),
            sa.column("site_name", sa.String),
            sa.column("site_description", sa.Text),
            sa.column("contact_email", sa.String),
            sa.column("posts_per_page", sa.Integer),
            sa.column("allow_comments", sa.Boolean),
            sa.column("allow_registration", sa.Boolean),
            sa.column("require_email_verification", sa.Boolean),
            sa.column("identity_label", sa.String),
            sa.column("breaking_label", sa.String),
            sa.column("daily_brief_label", sa.String),
            sa.column("daily_brief_url", sa.String),
            sa.column("social_links", sa.JSON),
            sa.column("ad_slot", sa.JSON),
            sa.column("market_watchlist", sa.JSON),
            sa.column("market_cache", sa.JSON),
            sa.column("spotlight_items", sa.JSON),
        ),
        [
            {
                "uuid": str(uuid4()),
                "singleton_key": "default",
                "site_name": "CraftyXHub",
                "site_description": "",
                "contact_email": "",
                "posts_per_page": 10,
                "allow_comments": True,
                "allow_registration": True,
                "require_email_verification": True,
                "identity_label": "GLOBAL WATCH",
                "breaking_label": "BREAKING",
                "daily_brief_label": "DAILY BRIEF",
                "daily_brief_url": "/brief",
                "social_links": [
                    {"platform": "x", "label": "X", "url": ""},
                    {"platform": "facebook", "label": "Facebook", "url": ""},
                    {"platform": "instagram", "label": "Instagram", "url": ""},
                    {"platform": "linkedin", "label": "LinkedIn", "url": ""},
                ],
                "ad_slot": {
                    "enabled": True,
                    "mode": "placeholder",
                    "label": "ADVERTISEMENT",
                    "image_url": "",
                    "target_url": "",
                    "background_color": "#F4F6F8",
                },
                "market_watchlist": [
                    {"symbol": "BTC/USD", "label": "BTC/USD", "enabled": True},
                    {"symbol": "ETH/USD", "label": "ETH/USD", "enabled": True},
                    {"symbol": "IXIC", "label": "NASDAQ", "enabled": True},
                    {"symbol": "GSPC", "label": "S&P 500", "enabled": True},
                    {"symbol": "EUR/USD", "label": "EUR/USD", "enabled": True},
                ],
                "market_cache": [],
                "spotlight_items": [
                    {
                        "label": "AI PULSE",
                        "target_url": "/category/ai",
                        "icon": "sparkles",
                        "theme": "emerald",
                        "enabled": True,
                        "start_at": None,
                        "end_at": None,
                        "priority": 100,
                        "is_default": True,
                    }
                ],
            }
        ],
    )

    op.add_column(
        "posts",
        sa.Column(
            "is_breaking_news",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column("posts", sa.Column("breaking_news_order", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_posts_breaking_news_order"),
        "posts",
        ["is_breaking_news", "breaking_news_order"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_posts_breaking_news_order"), table_name="posts")
    op.drop_column("posts", "breaking_news_order")
    op.drop_column("posts", "is_breaking_news")

    op.drop_index(op.f("ix_site_settings_uuid"), table_name="site_settings")
    op.drop_table("site_settings")
