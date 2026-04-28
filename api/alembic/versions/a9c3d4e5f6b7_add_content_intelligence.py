"""add_content_intelligence

Revision ID: a9c3d4e5f6b7
Revises: 90d4b2f1aa11
Create Date: 2026-04-27 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a9c3d4e5f6b7"
down_revision = "90d4b2f1aa11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_content_sources_uuid"), "content_sources", ["uuid"], unique=True)
    op.create_index("ix_content_sources_source_type", "content_sources", ["source_type"])
    op.create_index("ix_content_sources_category_id", "content_sources", ["category_id"])

    op.create_table(
        "site_search_queries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("query", sa.String(length=255), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("session_key", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="public_search"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_site_search_queries_uuid"), "site_search_queries", ["uuid"], unique=True)
    op.create_index("ix_site_search_queries_query", "site_search_queries", ["query"])
    op.create_index("ix_site_search_queries_user_id", "site_search_queries", ["user_id"])
    op.create_index("ix_site_search_queries_session_key", "site_search_queries", ["session_key"])

    op.create_table(
        "topic_briefs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("angle", sa.Text(), nullable=True),
        sa.Column("audience", sa.String(length=255), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("source_signals", sa.JSON(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_topic_briefs_uuid"), "topic_briefs", ["uuid"], unique=True)
    op.create_index("ix_topic_briefs_status", "topic_briefs", ["status"])
    op.create_index("ix_topic_briefs_category_id", "topic_briefs", ["category_id"])
    op.create_index("ix_topic_briefs_created_by_id", "topic_briefs", ["created_by_id"])

    op.create_table(
        "post_quality_reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("checks", sa.JSON(), nullable=False),
        sa.Column("needs_human_review", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("score", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="needs_review"),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_post_quality_reviews_uuid"), "post_quality_reviews", ["uuid"], unique=True)
    op.create_index("ix_post_quality_reviews_post_id", "post_quality_reviews", ["post_id"])
    op.create_index("ix_post_quality_reviews_status", "post_quality_reviews", ["status"])
    op.create_index("ix_post_quality_reviews_approved_by_id", "post_quality_reviews", ["approved_by_id"])

    op.create_table(
        "distribution_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("asset_metadata", sa.JSON(), nullable=True),
        sa.Column("tracked_url", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_distribution_assets_uuid"), "distribution_assets", ["uuid"], unique=True)
    op.create_index("ix_distribution_assets_post_id", "distribution_assets", ["post_id"])
    op.create_index("ix_distribution_assets_platform", "distribution_assets", ["platform"])
    op.create_index("ix_distribution_assets_status", "distribution_assets", ["status"])

    op.create_table(
        "tracking_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("token", sa.String(length=80), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("distribution_asset_id", sa.Integer(), nullable=True),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("destination_url", sa.String(length=1000), nullable=False),
        sa.Column("utm_source", sa.String(length=100), nullable=True),
        sa.Column("utm_medium", sa.String(length=100), nullable=True),
        sa.Column("utm_campaign", sa.String(length=150), nullable=True),
        sa.Column("click_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["distribution_asset_id"], ["distribution_assets.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_tracking_links_uuid"), "tracking_links", ["uuid"], unique=True)
    op.create_index(op.f("ix_tracking_links_token"), "tracking_links", ["token"], unique=True)
    op.create_index("ix_tracking_links_post_id", "tracking_links", ["post_id"])
    op.create_index("ix_tracking_links_distribution_asset_id", "tracking_links", ["distribution_asset_id"])
    op.create_index("ix_tracking_links_platform", "tracking_links", ["platform"])

    op.create_table(
        "tracking_clicks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("tracking_link_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("ip_hash", sa.String(length=80), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("referrer", sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(["tracking_link_id"], ["tracking_links.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_tracking_clicks_uuid"), "tracking_clicks", ["uuid"], unique=True)
    op.create_index("ix_tracking_clicks_tracking_link_id", "tracking_clicks", ["tracking_link_id"])
    op.create_index("ix_tracking_clicks_user_id", "tracking_clicks", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_tracking_clicks_user_id", table_name="tracking_clicks")
    op.drop_index("ix_tracking_clicks_tracking_link_id", table_name="tracking_clicks")
    op.drop_index(op.f("ix_tracking_clicks_uuid"), table_name="tracking_clicks")
    op.drop_table("tracking_clicks")

    op.drop_index("ix_tracking_links_platform", table_name="tracking_links")
    op.drop_index("ix_tracking_links_distribution_asset_id", table_name="tracking_links")
    op.drop_index("ix_tracking_links_post_id", table_name="tracking_links")
    op.drop_index(op.f("ix_tracking_links_token"), table_name="tracking_links")
    op.drop_index(op.f("ix_tracking_links_uuid"), table_name="tracking_links")
    op.drop_table("tracking_links")

    op.drop_index("ix_distribution_assets_status", table_name="distribution_assets")
    op.drop_index("ix_distribution_assets_platform", table_name="distribution_assets")
    op.drop_index("ix_distribution_assets_post_id", table_name="distribution_assets")
    op.drop_index(op.f("ix_distribution_assets_uuid"), table_name="distribution_assets")
    op.drop_table("distribution_assets")

    op.drop_index("ix_post_quality_reviews_approved_by_id", table_name="post_quality_reviews")
    op.drop_index("ix_post_quality_reviews_status", table_name="post_quality_reviews")
    op.drop_index("ix_post_quality_reviews_post_id", table_name="post_quality_reviews")
    op.drop_index(op.f("ix_post_quality_reviews_uuid"), table_name="post_quality_reviews")
    op.drop_table("post_quality_reviews")

    op.drop_index("ix_topic_briefs_created_by_id", table_name="topic_briefs")
    op.drop_index("ix_topic_briefs_category_id", table_name="topic_briefs")
    op.drop_index("ix_topic_briefs_status", table_name="topic_briefs")
    op.drop_index(op.f("ix_topic_briefs_uuid"), table_name="topic_briefs")
    op.drop_table("topic_briefs")

    op.drop_index("ix_site_search_queries_session_key", table_name="site_search_queries")
    op.drop_index("ix_site_search_queries_user_id", table_name="site_search_queries")
    op.drop_index("ix_site_search_queries_query", table_name="site_search_queries")
    op.drop_index(op.f("ix_site_search_queries_uuid"), table_name="site_search_queries")
    op.drop_table("site_search_queries")

    op.drop_index("ix_content_sources_category_id", table_name="content_sources")
    op.drop_index("ix_content_sources_source_type", table_name="content_sources")
    op.drop_index(op.f("ix_content_sources_uuid"), table_name="content_sources")
    op.drop_table("content_sources")
