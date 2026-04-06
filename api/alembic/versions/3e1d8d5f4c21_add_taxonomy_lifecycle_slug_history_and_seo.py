"""add taxonomy lifecycle slug history and seo

Revision ID: 3e1d8d5f4c21
Revises: f1c9e7a4b2d0
Create Date: 2026-04-07 11:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e1d8d5f4c21"
down_revision = "f1c9e7a4b2d0"
branch_labels = None
depends_on = None


categories = sa.table(
    "categories",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
    sa.column("slug", sa.String(length=100)),
    sa.column("description", sa.Text()),
    sa.column("parent_id", sa.Integer()),
)


def _fetch_category_id(connection, name: str, parent_id: int | None = None):
    query = sa.select(categories.c.id).where(categories.c.name == name)
    if parent_id is None:
        query = query.where(categories.c.parent_id.is_(None))
    else:
        query = query.where(categories.c.parent_id == parent_id)
    return connection.execute(query).scalar_one_or_none()


def _ensure_category(
    connection,
    *,
    parent_name: str,
    name: str,
    slug: str,
    description: str | None = None,
) -> None:
    parent_id = _fetch_category_id(connection, parent_name, None)
    if parent_id is None:
        return

    existing_id = _fetch_category_id(connection, name, parent_id)
    if existing_id is not None:
        return

    connection.execute(
        categories.insert().values(
            name=name,
            slug=slug,
            description=description,
            parent_id=parent_id,
        )
    )


def _seed_slug_history(connection) -> None:
    connection.execute(
        sa.text(
            """
            INSERT INTO category_slug_history (category_id, slug)
            SELECT c.id, c.slug
            FROM categories c
            WHERE c.slug IS NOT NULL
              AND c.slug <> ''
              AND NOT EXISTS (
                SELECT 1
                FROM category_slug_history h
                WHERE h.slug = c.slug
              )
            """
        )
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO tag_slug_history (tag_id, slug)
            SELECT t.id, t.slug
            FROM tags t
            WHERE t.slug IS NOT NULL
              AND t.slug <> ''
              AND NOT EXISTS (
                SELECT 1
                FROM tag_slug_history h
                WHERE h.slug = t.slug
              )
            """
        )
    )


def upgrade() -> None:
    op.add_column(
        "tags",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "tags",
        sa.Column("canonical_tag_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_tags_canonical_tag_id_tags",
        "tags",
        "tags",
        ["canonical_tag_id"],
        ["id"],
    )

    op.add_column("posts", sa.Column("seo_keywords", sa.JSON(), nullable=True))

    op.create_table(
        "category_slug_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_category_slug_history_category_id",
        "category_slug_history",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "ix_category_slug_history_slug",
        "category_slug_history",
        ["slug"],
        unique=True,
    )

    op.create_table(
        "tag_slug_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_tag_slug_history_tag_id",
        "tag_slug_history",
        ["tag_id"],
        unique=False,
    )
    op.create_index(
        "ix_tag_slug_history_slug",
        "tag_slug_history",
        ["slug"],
        unique=True,
    )

    connection = op.get_bind()
    _ensure_category(
        connection,
        parent_name="Tech & Innovation",
        name="Products & Platforms",
        slug="products-and-platforms",
        description="Product previews, platform launches, reviews, and comparisons.",
    )
    _ensure_category(
        connection,
        parent_name="Business & Finance",
        name="Business News & Market Intelligence",
        slug="business-news-and-market-intelligence",
        description="Business current-affairs, market signals, company risk, and valuation analysis.",
    )
    _seed_slug_history(connection)

    op.alter_column("tags", "is_active", server_default=None)


def downgrade() -> None:
    connection = op.get_bind()
    tech_parent_id = _fetch_category_id(connection, "Tech & Innovation", None)
    business_parent_id = _fetch_category_id(connection, "Business & Finance", None)

    if tech_parent_id is not None:
        connection.execute(
            categories.delete().where(
                categories.c.name == "Products & Platforms",
                categories.c.parent_id == tech_parent_id,
            )
        )
    if business_parent_id is not None:
        connection.execute(
            categories.delete().where(
                categories.c.name == "Business News & Market Intelligence",
                categories.c.parent_id == business_parent_id,
            )
        )

    op.drop_index("ix_tag_slug_history_slug", table_name="tag_slug_history")
    op.drop_index("ix_tag_slug_history_tag_id", table_name="tag_slug_history")
    op.drop_table("tag_slug_history")

    op.drop_index("ix_category_slug_history_slug", table_name="category_slug_history")
    op.drop_index("ix_category_slug_history_category_id", table_name="category_slug_history")
    op.drop_table("category_slug_history")

    op.drop_column("posts", "seo_keywords")

    op.drop_constraint("fk_tags_canonical_tag_id_tags", "tags", type_="foreignkey")
    op.drop_column("tags", "canonical_tag_id")
    op.drop_column("tags", "is_active")
