"""set_market_watch_defaults

Revision ID: e7f8a9b0c1d2
Revises: d4e5f6a7b8c9
Create Date: 2026-04-29 18:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e7f8a9b0c1d2"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


OLD_DEFAULT_WATCHLIST = [
    {"symbol": "BTC/USD", "label": "BTC/USD", "enabled": True},
    {"symbol": "ETH/USD", "label": "ETH/USD", "enabled": True},
    {"symbol": "IXIC", "label": "NASDAQ", "enabled": True},
    {"symbol": "GSPC", "label": "S&P 500", "enabled": True},
    {"symbol": "EUR/USD", "label": "EUR/USD", "enabled": True},
]

NEW_DEFAULT_WATCHLIST = [
    {"symbol": "IXIC", "label": "NASDAQ", "enabled": True},
    {"symbol": "GSPC", "label": "S&P 500", "enabled": True},
    {"symbol": "BTC/USD", "label": "BTC", "enabled": True},
    {"symbol": "ETH/USD", "label": "ETH", "enabled": True},
    {"symbol": "EUR/USD", "label": "EUR/USD", "enabled": True},
    {"symbol": "GBP/USD", "label": "GBP/USD", "enabled": True},
]


def upgrade() -> None:
    bind = op.get_bind()
    site_settings = sa.table(
        "site_settings",
        sa.column("id", sa.Integer),
        sa.column("identity_label", sa.String),
        sa.column("market_watchlist", sa.JSON),
    )

    rows = bind.execute(
        sa.select(
            site_settings.c.id,
            site_settings.c.identity_label,
            site_settings.c.market_watchlist,
        )
    ).mappings()

    for row in rows:
        updates = {}
        if row["identity_label"] == "GLOBAL WATCH":
            updates["identity_label"] = "MARKET WATCH"
        if row["market_watchlist"] == OLD_DEFAULT_WATCHLIST:
            updates["market_watchlist"] = NEW_DEFAULT_WATCHLIST

        if updates:
            bind.execute(
                site_settings.update()
                .where(site_settings.c.id == row["id"])
                .values(**updates)
            )


def downgrade() -> None:
    bind = op.get_bind()
    site_settings = sa.table(
        "site_settings",
        sa.column("id", sa.Integer),
        sa.column("identity_label", sa.String),
        sa.column("market_watchlist", sa.JSON),
    )

    rows = bind.execute(
        sa.select(
            site_settings.c.id,
            site_settings.c.identity_label,
            site_settings.c.market_watchlist,
        )
    ).mappings()

    for row in rows:
        updates = {}
        if row["identity_label"] == "MARKET WATCH":
            updates["identity_label"] = "GLOBAL WATCH"
        if row["market_watchlist"] == NEW_DEFAULT_WATCHLIST:
            updates["market_watchlist"] = OLD_DEFAULT_WATCHLIST

        if updates:
            bind.execute(
                site_settings.update()
                .where(site_settings.c.id == row["id"])
                .values(**updates)
            )
