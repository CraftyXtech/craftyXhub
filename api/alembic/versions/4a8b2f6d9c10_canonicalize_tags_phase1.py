"""canonicalize tags phase 1

Revision ID: 4a8b2f6d9c10
Revises: 3e1d8d5f4c21
Create Date: 2026-04-07 11:40:00.000000

"""

from alembic import op
import sqlalchemy as sa
import re
import unicodedata


# revision identifiers, used by Alembic.
revision = "4a8b2f6d9c10"
down_revision = "3e1d8d5f4c21"
branch_labels = None
depends_on = None


categories = sa.table(
    "categories",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
)

tags = sa.table(
    "tags",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=50)),
    sa.column("slug", sa.String(length=50)),
    sa.column("category_id", sa.Integer()),
    sa.column("is_active", sa.Boolean()),
    sa.column("canonical_tag_id", sa.Integer()),
)

tag_slug_history = sa.table(
    "tag_slug_history",
    sa.column("tag_id", sa.Integer()),
    sa.column("slug", sa.String(length=50)),
)

post_tags = sa.table(
    "post_tags",
    sa.column("post_id", sa.Integer()),
    sa.column("tag_id", sa.Integer()),
)


CANONICAL_TAG_DEFINITIONS = {
    "Automation": "Automation",
    "Freelancing": "Freelancing",
    "Online Learning": "Learning & Skill Building",
    "Productivity Tools": "Productivity & Remote Work",
    "Creator Platforms": "Creator Business",
    "Social Media Strategy": "Personal Brand & Audience",
    "Remote Work": "Productivity & Remote Work",
    "Financial Independence": "Personal Finance & Investing",
    "Intentional Living": "Intentional Living",
    "Personal Growth": "Personal Growth",
    "Personal Branding": "Personal Brand & Audience",
    "Professional Portfolio": "Personal Brand & Audience",
}

TAG_MAPPINGS = {
    "Zapier": "Automation",
    "Make": "Automation",
    "n8n": "Automation",
    "Workflows": "Automation",
    "Fiverr": "Freelancing",
    "Upwork": "Freelancing",
    "Coursera": "Online Learning",
    "Udemy": "Online Learning",
    "Notion": "Productivity Tools",
    "Obsidian": "Productivity Tools",
    "Patreon": "Creator Platforms",
    "Substack": "Creator Platforms",
    "YouTube": "Creator Platforms",
    "Podcasting": "Creator Platforms",
    "Newsletter": "Creator Platforms",
    "Twitter": "Social Media Strategy",
    "Social Media": "Social Media Strategy",
    "Work From Home": "Remote Work",
    "Productivity Apps": "Productivity Tools",
    "FIRE": "Financial Independence",
    "Simple Living": "Intentional Living",
    "Personal Development": "Personal Growth",
    "Self-Improvement": "Personal Growth",
    "Online Presence": "Personal Branding",
    "Thought Leadership": "Personal Branding",
    "LinkedIn": "Personal Branding",
    "Portfolio": "Professional Portfolio",
}


def _slugify(value: str, *, max_length: int = 50) -> str:
    slug = unicodedata.normalize("NFKD", value.strip().lower())
    slug = "".join(char for char in slug if not unicodedata.combining(char))
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_length].strip("-")


def _fetch_category_id(connection, name: str):
    return connection.execute(
        sa.select(categories.c.id).where(categories.c.name == name)
    ).scalar_one_or_none()


def _fetch_tag(connection, name: str):
    row = connection.execute(
        sa.select(
            tags.c.id,
            tags.c.name,
            tags.c.slug,
            tags.c.category_id,
            tags.c.is_active,
            tags.c.canonical_tag_id,
        ).where(tags.c.name == name)
    ).mappings().first()
    return row


def _ensure_canonical_tag(connection, tag_name: str) -> int | None:
    existing = _fetch_tag(connection, tag_name)
    if existing is not None:
        connection.execute(
            tags.update()
            .where(tags.c.id == existing["id"])
            .values(is_active=True, canonical_tag_id=None)
        )
        connection.execute(
            sa.text(
                """
                INSERT INTO tag_slug_history (tag_id, slug)
                SELECT :tag_id, :slug
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM tag_slug_history
                    WHERE tag_id = :tag_id
                      AND slug = :slug
                )
                """
            ),
            {"tag_id": existing["id"], "slug": existing["slug"]},
        )
        return existing["id"]

    category_name = CANONICAL_TAG_DEFINITIONS.get(tag_name)
    if category_name is None:
        return None

    category_id = _fetch_category_id(connection, category_name)
    if category_id is None:
        return None

    result = connection.execute(
        tags.insert().values(
            name=tag_name,
            slug=_slugify(tag_name),
            category_id=category_id,
            is_active=True,
            canonical_tag_id=None,
        ).returning(tags.c.id)
    )
    tag_id = result.scalar_one()
    connection.execute(
        tag_slug_history.insert().values(tag_id=tag_id, slug=_slugify(tag_name))
    )
    return tag_id


def _merge_tag(connection, old_tag_name: str, canonical_tag_name: str) -> None:
    old_tag = _fetch_tag(connection, old_tag_name)
    canonical_id = _ensure_canonical_tag(connection, canonical_tag_name)
    if old_tag is None or canonical_id is None or old_tag["id"] == canonical_id:
        return

    connection.execute(
        sa.text(
            """
            INSERT INTO post_tags (post_id, tag_id)
            SELECT pt.post_id, :canonical_tag_id
            FROM post_tags pt
            WHERE pt.tag_id = :old_tag_id
              AND NOT EXISTS (
                SELECT 1
                FROM post_tags existing
                WHERE existing.post_id = pt.post_id
                  AND existing.tag_id = :canonical_tag_id
              )
            """
        ),
        {"old_tag_id": old_tag["id"], "canonical_tag_id": canonical_id},
    )
    connection.execute(
        post_tags.delete().where(post_tags.c.tag_id == old_tag["id"])
    )
    connection.execute(
        tags.update()
        .where(tags.c.id == old_tag["id"])
        .values(is_active=False, canonical_tag_id=canonical_id)
    )


def upgrade() -> None:
    connection = op.get_bind()
    for canonical_tag_name in CANONICAL_TAG_DEFINITIONS:
        _ensure_canonical_tag(connection, canonical_tag_name)

    for old_tag_name, canonical_tag_name in TAG_MAPPINGS.items():
        _merge_tag(connection, old_tag_name, canonical_tag_name)


def downgrade() -> None:
    connection = op.get_bind()

    for old_tag_name, canonical_tag_name in TAG_MAPPINGS.items():
        old_tag = _fetch_tag(connection, old_tag_name)
        canonical_tag = _fetch_tag(connection, canonical_tag_name)
        if old_tag is None:
            continue

        if canonical_tag is not None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO post_tags (post_id, tag_id)
                    SELECT pt.post_id, :old_tag_id
                    FROM post_tags pt
                    WHERE pt.tag_id = :canonical_tag_id
                      AND NOT EXISTS (
                        SELECT 1
                        FROM post_tags existing
                        WHERE existing.post_id = pt.post_id
                          AND existing.tag_id = :old_tag_id
                      )
                    """
                ),
                {
                    "old_tag_id": old_tag["id"],
                    "canonical_tag_id": canonical_tag["id"],
                },
            )

        connection.execute(
            tags.update()
            .where(tags.c.id == old_tag["id"])
            .values(is_active=True, canonical_tag_id=None)
        )
